#!/usr/bin/perl

use strict;
use warnings;
use utf8;

use POSIX qw(strftime);
use Time::Local qw(timegm);
use File::Path qw(make_path);
use Fcntl qw(:flock);
use JSON qw(encode_json decode_json);

use lib "/opt/loxberry/bin/plugins/fyta_connect";

use config;
use auth_store;
use fyta_api;
use logger;
use udp;

my $INVALID_VALUE = -9999;

my $DATA_DIR = "/opt/loxberry/data/plugins/fyta_connect";
my $STATUS_FILE = "$DATA_DIR/status.cfg";
my $PLANTS_CACHE_FILE = "$DATA_DIR/plants_cache.json";
my $SENSOR_META_FILE = "$DATA_DIR/sensor_meta.json";
my $WORKER_LOCK_FILE = "$DATA_DIR/worker.lock";

make_path($DATA_DIR, { mode => 0750 }) unless -d $DATA_DIR;
open(my $worker_lock_fh, ">>", $WORKER_LOCK_FILE)
    or die "Kann Worker-Sperrdatei nicht öffnen: $!\n";
unless (flock($worker_lock_fh, LOCK_EX | LOCK_NB)) {
    logger::info("Worker läuft bereits – paralleler Start wird übersprungen");
    exit 0;
}

my $start_epoch = time();
my $plant_count = 0;
my $telegram_count = 0;
my $invalid_value_count = 0;
my $error_count = 0;
my $used_plant_cache = 0;
my $last_error = "";
my @sensor_meta;
my $previous_sensor_meta = load_sensor_meta();

logger::info("FYTA Connect gestartet");

my $previous_status = read_key_value_file($STATUS_FILE);
my $cfg = config::read_config();

unless ($cfg && ref($cfg) eq "HASH") {
    finish_with_error("Konfiguration konnte nicht gelesen werden");
}

unless (($cfg->{PLUGIN_ENABLED} // "true") eq "true") {
    logger::info("Plugin ist deaktiviert – keine Synchronisation ausgeführt");
    write_status({
        LAST_RUN_EPOCH => time(),
        LAST_RUN => timestamp(time()),
        STATUS => "DISABLED",
        MESSAGE => "Plugin ist deaktiviert",
        PLANTS => 0, TELEGRAMS => 0, ERRORS => 0, INVALID_VALUES => 0,
        DURATION_SECONDS => time() - $start_epoch,
    });
    exit 0;
}

# Vorhandenen Legacy-Token einmalig in den geschützten Auth-Speicher übernehmen.
# Erst wenn das erfolgreich war, wird er aus der normalen Konfiguration entfernt.
my $legacy_token = $cfg->{FYTA_TOKEN} // "";
if (length $legacy_token) {
    my $imported = eval { auth_store::import_legacy_token($legacy_token) };
    if ($imported) {
        $cfg->{FYTA_TOKEN} = '';
        eval { config::write_config($cfg); };
        logger::info("Vorhandener FYTA-Token wurde in den geschützten Auth-Speicher migriert") unless $@;
    }
}

my $token = resolve_access_token($cfg, 0);
my $host = $cfg->{UDP_HOST} // "";
my $port = $cfg->{UDP_PORT} // "";
my $udp_enabled = ($cfg->{UDP_ENABLED} // "false") eq "true";

unless (length $token) {
    finish_with_error("Keine gültige FYTA-Anmeldung vorhanden – bitte Zugangsdaten unter Einstellungen hinterlegen");
}
unless (length $host) {
    finish_with_error("Kein UDP-Ziel gespeichert");
}
unless ($port =~ /^\d+$/ && $port >= 1 && $port <= 65535) {
    finish_with_error("Ungültiger UDP-Port");
}
unless ($udp_enabled) {
    finish_with_error("UDP ist in der Konfiguration deaktiviert");
}

logger::info("UDP-Ziel: $host:$port");

my $plants = fyta_api::get_plants($token);
if ((!$plants || ref($plants) ne "ARRAY") && fyta_api::last_http_status() == 401) {
    logger::warning("FYTA-Token wurde abgewiesen – automatische Neuanmeldung wird versucht");
    my $renewed = resolve_access_token($cfg, 1);
    if (length $renewed) {
        $token = $renewed;
        $plants = fyta_api::get_plants($token);
    }
}

if ($plants && ref($plants) eq "ARRAY" && @{$plants}) {
    save_plants_cache($plants);
}
else {
    $plants = load_plants_cache();

    unless ($plants && ref($plants) eq "ARRAY" && @{$plants}) {
        finish_with_error(
            "Pflanzenliste konnte nicht abgerufen werden und es ist kein Cache vorhanden"
        );
    }

    $used_plant_cache = 1;
    logger::warning(
        "Pflanzenliste nicht abrufbar – verwende den zuletzt gespeicherten Pflanzen-Cache"
    );
}

$plant_count = scalar @{$plants};
logger::info("$plant_count Pflanzen gefunden");

foreach my $plant (@{$plants}) {
    my $plant_id = $plant->{id};
    my $plant_name = $plant->{nickname} // $plant->{name} // "Unbekannt";

    logger::info("Lese Pflanze: $plant_name ($plant_id)");

    my $data = fyta_api::get_plant_details($token, $plant_id);
    if (!$data && fyta_api::last_http_status() == 401) {
        logger::warning("FYTA-Token bei Detailabruf abgewiesen – automatische Neuanmeldung wird versucht");
        my $renewed = resolve_access_token($cfg, 1);
        if (length $renewed) {
            $token = $renewed;
            $data = fyta_api::get_plant_details($token, $plant_id);
        }
    }
    my $name = normalize($plant_name);

    my %values;
    my $freshness = 0;
    my $sensor_id = '';
    my $sensor_type = 'Unbekannt';
    my $sensor_type_id = '';
    my $device_type = '';
    my $sensor_version = '';

    if ($data && ref($data) eq "HASH") {
        $name = normalize($data->{name} // $plant_name);
        $sensor_id = defined $data->{sensor} ? "$data->{sensor}" : '';
        $sensor_type = $data->{sensor_type} // 'Unbekannt';
        $sensor_type_id = defined $data->{sensor_type_id} ? "$data->{sensor_type_id}" : '';
        $device_type = defined $data->{device_type} ? "$data->{device_type}" : '';
        $sensor_version = defined $data->{sensor_version} ? "$data->{sensor_version}" : '';
        %values = (
            Temperature => $data->{temperature},
            Moisture    => $data->{moisture},
            Light       => $data->{light},
            Salinity    => $data->{salinity},
            Battery     => $data->{battery},
        );
    }
    else {
        logger::warning(
            "Keine Detaildaten für $plant_name – sende alle Messwerte mit $INVALID_VALUE"
        );

        %values = map { $_ => undef } qw(
            Temperature Moisture Light Salinity Battery
        );

        my $old = previous_sensor_for_plant($previous_sensor_meta, $plant_id);
        if ($old) {
            $sensor_id = $old->{sensor_id} // '';
            $sensor_type = $old->{sensor_type} // 'Unbekannt';
            $sensor_type_id = $old->{sensor_type_id} // '';
            $device_type = $old->{device_type} // '';
            $sensor_version = $old->{sensor_version} // '';
        }
    }

    my $config_id = sensor_config_id($sensor_id, $plant_id);
    my $plant_config_id = plant_config_id($plant_id);
    my $recommendation = recommended_age_hours($sensor_type);
    my $hours_key = "CURRENT_MAX_AGE_HOURS_$config_id";
    my $send_key = "SEND_CURRENT_$plant_config_id";
    my $legacy_send_key = "SEND_CURRENT_$config_id";
    my $freshness_hours = $cfg->{$hours_key};
    $freshness_hours = $recommendation
        unless defined $freshness_hours && $freshness_hours =~ /^\d+(?:\.\d+)?$/ && $freshness_hours > 0;

    # Die UDP-Ausgabe *_Aktuell gehört zur Pflanze, nicht zur austauschbaren Sensor-ID.
    # Neue Konfigurationen verwenden deshalb eine stabile Pflanzen-ID. Vorhandene
    # bestehende 1.8.x-Einstellungen werden transparent aus dem alten Sensor-Schlüssel gelesen.
    my $send_setting;
    if (defined $cfg->{$send_key} && $cfg->{$send_key} ne '') {
        $send_setting = $cfg->{$send_key};
    } elsif (defined $cfg->{$legacy_send_key} && $cfg->{$legacy_send_key} ne '') {
        $send_setting = $cfg->{$legacy_send_key};
    } else {
        $send_setting = 'true';
    }
    my $send_current = lc($send_setting // 'true') =~ /^(?:true|1|yes|on)$/ ? 1 : 0;

    $freshness = sensor_is_current($data ? $data->{received} : undef, $freshness_hours) ? 1 : 0;

    push @sensor_meta, {
        plant_id => $plant_id,
        plant_name => $plant_name,
        sensor_id => $sensor_id,
        sensor_type => $sensor_type,
        sensor_type_id => $sensor_type_id,
        device_type => $device_type,
        sensor_version => $sensor_version,
        config_id => $config_id,
        plant_config_id => $plant_config_id,
        recommended_hours => $recommendation,
        configured_hours => $freshness_hours + 0,
        send_current => $send_current ? 1 : 0,
        received_data_at => $data ? ($data->{received} // '') : '',
    };

    logger::info(
        "Aktualität $plant_name: " . ($freshness ? "aktuell" : "veraltet")
        . " (Grenze ${freshness_hours}h, Empfehlung ${recommendation}h, Sensor=$sensor_type, received_data_at="
        . ($data && defined $data->{received} ? $data->{received} : "nicht vorhanden") . ")"
    );

    foreach my $field (sort keys %values) {
        my $value = $values{$field};

        if (!is_valid_value($value)) {
            $value = $INVALID_VALUE;
            $invalid_value_count++;

            logger::warning(
                "Kein gültiger Messwert für $plant_name / $field – sende $INVALID_VALUE"
            );
        }

        my $telegram = "FYTA_${name}_${field}=$value";
        my $result = udp::send_udp($host, $port, $telegram);

        if (defined $result && $result =~ /^OK\b/i) {
            $telegram_count++;
            logger::info("UDP gesendet: $telegram");
        }
        else {
            $error_count++;

            my $udp_error =
                defined $result && length $result
                ? $result
                : "Keine Rückmeldung";

            $last_error = "UDP-Fehler bei $telegram: $udp_error";
            logger::error($last_error);
        }
    }

    # Eigener 0/1-Aktualitätswert pro Pflanze/Sensor, pro Sensor konfigurierbar.
    if ($send_current) {
        my $freshness_telegram = "FYTA_${name}_Aktuell=$freshness";
        my $freshness_result = udp::send_udp($host, $port, $freshness_telegram);

        if (defined $freshness_result && $freshness_result =~ /^OK\b/i) {
            $telegram_count++;
            logger::info("UDP gesendet: $freshness_telegram");
        }
        else {
            $error_count++;
            my $udp_error =
                defined $freshness_result && length $freshness_result
                ? $freshness_result
                : "Keine Rückmeldung";
            $last_error = "UDP-Fehler bei $freshness_telegram: $udp_error";
            logger::error($last_error);
        }
    }
    else {
        logger::debug("Aktualitätswert für $plant_name ist deaktiviert");
    }
}

save_sensor_meta(\@sensor_meta) if @sensor_meta;

# Globaler Heartbeat: 1 bedeutet, dass der Plugin-Lauf die FYTA-Daten verarbeitet hat.
my $heartbeat_result = udp::send_udp($host, $port, "FYTA_Heartbeat=1");
if (defined $heartbeat_result && $heartbeat_result =~ /^OK\b/i) {
    $telegram_count++;
    logger::info("UDP gesendet: FYTA_Heartbeat=1");
}
else {
    $error_count++;
    my $udp_error = defined $heartbeat_result && length $heartbeat_result ? $heartbeat_result : "Keine Rückmeldung";
    $last_error = "UDP-Fehler bei FYTA_Heartbeat=1: $udp_error";
    logger::error($last_error);
}

my $duration = time() - $start_epoch;
my $now = time();
my $run_status;
my $message;

if ($telegram_count == 0 || $error_count > 0) {
    $run_status = "ERROR";
    $message = $last_error || "Keine UDP-Telegramme erfolgreich gesendet";
}
elsif ($invalid_value_count > 0 || $used_plant_cache) {
    $run_status = "WARNING";
    $message = "$telegram_count Telegramme gesendet, davon $invalid_value_count Ersatzwerte ($INVALID_VALUE)";
}
else {
    $run_status = "OK";
    $message = "$telegram_count Telegramme erfolgreich gesendet";
}

my $last_success_epoch = $previous_status->{LAST_SUCCESS_EPOCH} // "";
my $last_success = $previous_status->{LAST_SUCCESS} // "";

if ($run_status eq "OK") {
    $last_success_epoch = $now;
    $last_success = timestamp($now);
}

write_status({
    LAST_RUN_EPOCH      => $now,
    LAST_RUN            => timestamp($now),
    LAST_SEND_EPOCH     => $telegram_count > 0 ? $now : ($previous_status->{LAST_SEND_EPOCH} // ""),
    LAST_SEND           => $telegram_count > 0 ? timestamp($now) : ($previous_status->{LAST_SEND} // ""),
    LAST_SUCCESS_EPOCH  => $last_success_epoch,
    LAST_SUCCESS        => $last_success,
    PLANTS              => $plant_count,
    TELEGRAMS           => $telegram_count,
    INVALID_VALUES      => $invalid_value_count,
    ERRORS              => $error_count,
    USED_PLANT_CACHE    => $used_plant_cache,
    INVALID_VALUE       => $INVALID_VALUE,
    DURATION_SECONDS    => $duration,
    STATUS              => $run_status,
    MESSAGE             => $message,
});

if ($run_status eq "OK") {
    logger::info(
        "Synchronisation erfolgreich: $plant_count Pflanzen, "
        . "$telegram_count Telegramme, ${duration}s"
    );
    exit 0;
}

if ($run_status eq "WARNING") {
    logger::warning(
        "Synchronisation mit Ersatzwerten beendet: $plant_count Pflanzen, "
        . "$telegram_count Telegramme, $invalid_value_count Ersatzwerte, ${duration}s"
    );
    exit 0;
}

logger::error("Synchronisation mit $error_count Fehlern beendet");
exit 1;

sub sensor_is_current
{
    my ($timestamp_text, $max_age_hours) = @_;

    my $epoch = parse_iso8601_epoch($timestamp_text);
    return 0 unless defined $epoch;

    my $age = time() - $epoch;

    # Deutlich in der Zukunft liegende Zeitstempel gelten ebenfalls als ungültig.
    return 0 if $age < -300;
    $age = 0 if $age < 0;

    $max_age_hours = 6 unless defined $max_age_hours && $max_age_hours > 0;
    return $age <= ($max_age_hours * 60 * 60) ? 1 : 0;
}

sub sensor_config_id
{
    my ($sensor_id, $plant_id) = @_;
    my $id = defined $sensor_id && length $sensor_id ? "SENSOR_$sensor_id" : "PLANT_$plant_id";
    $id =~ s/[^A-Za-z0-9_]/_/g;
    return uc($id);
}

sub plant_config_id
{
    my ($plant_id) = @_;
    my $id = "PLANT_" . (defined $plant_id ? $plant_id : 'UNKNOWN');
    $id =~ s/[^A-Za-z0-9_]/_/g;
    return uc($id);
}

sub recommended_age_hours
{
    my ($sensor_type) = @_;
    my $type = lc($sensor_type // '');

    return 3 if $type =~ /beam/ && $type =~ /(?:g1|gen(?:eration)?\s*1|generation_?1)/;
    return 2 if $type =~ /beam/ && $type =~ /(?:g2|gen(?:eration)?\s*2|generation_?2)/;
    return 2 if $type =~ /(?:terra|mini|sphere)/;
    return 2 if $type =~ /beam/;
    return 6;
}

sub previous_sensor_for_plant
{
    my ($list, $plant_id) = @_;
    return undef unless ref($list) eq 'ARRAY';
    for my $item (@{$list}) {
        next unless ref($item) eq 'HASH';
        return $item if defined $item->{plant_id} && "$item->{plant_id}" eq "$plant_id";
    }
    return undef;
}

sub load_sensor_meta
{
    return [] unless -f $SENSOR_META_FILE;
    open(my $fh, '<', $SENSOR_META_FILE) or return [];
    local $/;
    my $content = <$fh>;
    close $fh;
    my $data;
    eval { $data = decode_json($content); };
    return [] if $@ || ref($data) ne 'ARRAY';
    return $data;
}

sub save_sensor_meta
{
    my ($list) = @_;
    return unless ref($list) eq 'ARRAY';
    ensure_data_dir();
    my $temp = "$SENSOR_META_FILE.tmp.$$";
    if (open(my $fh, '>', $temp)) {
        print {$fh} encode_json($list);
        close $fh;
        rename($temp, $SENSOR_META_FILE)
            or logger::warning("Sensor-Metadaten konnten nicht ersetzt werden: $!");
    }
}

sub parse_iso8601_epoch
{
    my ($text) = @_;
    return undef unless defined $text && !ref($text);

    $text =~ s/^\s+//;
    $text =~ s/\s+$//;

    return undef unless $text =~
        /^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(Z|[+-]\d{2}:?\d{2})?$/;

    my ($year, $month, $day, $hour, $minute, $second, $zone) =
        ($1, $2, $3, $4, $5, $6, $7);

    my $epoch;
    eval {
        $epoch = timegm($second, $minute, $hour, $day, $month - 1, $year);
    };
    return undef if $@ || !defined $epoch;

    if (defined $zone && $zone ne '' && $zone ne 'Z') {
        my ($sign, $zh, $zm) = $zone =~ /^([+-])(\d{2}):?(\d{2})$/;
        return undef unless defined $sign;
        my $offset = ($zh * 60 + $zm) * 60;
        $epoch -= $sign eq '+' ? $offset : -$offset;
    }

    return $epoch;
}

sub is_valid_value
{
    my ($value) = @_;

    return 0 unless defined $value;
    return 0 if ref($value);

    my $text = "$value";
    $text =~ s/^\s+//;
    $text =~ s/\s+$//;

    return 0 if $text eq "";
    return 0 if lc($text) eq "null";
    return 0 if lc($text) eq "n/a";
    return 0 unless $text =~ /^-?(?:\d+(?:\.\d+)?|\.\d+)$/;

    return 1;
}

sub resolve_access_token
{
    my ($cfg, $force_login) = @_;
    my $auth = auth_store::load_auth();
    my $token = $auth->{access_token} // '';
    my $expires_at = $auth->{expires_at} // 0;
    my $email = $cfg->{FYTA_EMAIL} // ($auth->{email} // '');

    # Token mindestens eine Stunde vor Ablauf erneuern. Für migrierte Alt-Tokens
    # ohne bekannte Ablaufzeit wird erst bei HTTP 401 neu angemeldet.
    my $needs_login = $force_login ? 1 : 0;
    $needs_login = 1 if !length($token);
    $needs_login = 1 if $expires_at =~ /^\d+$/ && $expires_at > 0 && $expires_at <= time() + 3600;

    return $token unless $needs_login;
    return $token unless length $email && auth_store::has_password();

    my $password = eval { auth_store::load_password() };
    if ($@ || !defined($password) || !length($password)) {
        logger::error("Gespeichertes FYTA-Passwort konnte nicht entschlüsselt werden");
        return $force_login ? '' : $token;
    }

    logger::info("FYTA-Anmeldung wird erneuert");
    my $login = fyta_api::login($email, $password);
    unless ($login && ref($login) eq 'HASH') {
        logger::error(fyta_api::last_error() || 'FYTA-Anmeldung fehlgeschlagen');
        return $force_login ? '' : $token;
    }

    my $expires_in = $login->{expires_in};
    $expires_in = 0 unless defined $expires_in && $expires_in =~ /^\d+$/;
    my $new_expires_at = $expires_in > 0 ? time() + $expires_in : 0;
    eval {
        auth_store::store_session(
            email => $email,
            access_token => $login->{access_token},
            refresh_token => ($login->{refresh_token} // ''),
            expires_at => $new_expires_at,
        );
    };
    if ($@) {
        logger::error("Neue FYTA-Sitzung konnte nicht sicher gespeichert werden");
        return $force_login ? '' : $token;
    }

    logger::info("FYTA-Anmeldung erfolgreich erneuert");
    return $login->{access_token} // '';
}

sub finish_with_error
{
    my ($message) = @_;
    my $now = time();

    logger::error($message);

    if (defined $host && length $host && defined $port && $port =~ /^\d+$/ && $port >= 1 && $port <= 65535) {
        my $heartbeat_result = udp::send_udp($host, $port, "FYTA_Heartbeat=0");
        logger::info("UDP gesendet: FYTA_Heartbeat=0")
            if defined $heartbeat_result && $heartbeat_result =~ /^OK\b/i;
    }

    write_status({
        LAST_RUN_EPOCH     => $now,
        LAST_RUN           => timestamp($now),
        LAST_SEND_EPOCH    => $previous_status->{LAST_SEND_EPOCH} // "",
        LAST_SEND          => $previous_status->{LAST_SEND} // "",
        LAST_SUCCESS_EPOCH => $previous_status->{LAST_SUCCESS_EPOCH} // "",
        LAST_SUCCESS       => $previous_status->{LAST_SUCCESS} // "",
        PLANTS             => $plant_count,
        TELEGRAMS          => $telegram_count,
        INVALID_VALUES     => $invalid_value_count,
        ERRORS             => $error_count + 1,
        USED_PLANT_CACHE   => $used_plant_cache,
        INVALID_VALUE      => $INVALID_VALUE,
        DURATION_SECONDS   => time() - $start_epoch,
        STATUS             => "ERROR",
        MESSAGE            => $message,
    });

    exit 1;
}

sub save_plants_cache
{
    my ($plants) = @_;

    ensure_data_dir();

    my @cache;
    foreach my $plant (@{$plants}) {
        next unless ref($plant) eq "HASH";
        next unless defined $plant->{id};

        push @cache, {
            id       => $plant->{id},
            nickname => $plant->{nickname} // $plant->{name} // "Unbekannt",
        };
    }

    return unless @cache;

    my $temp_file = "$PLANTS_CACHE_FILE.tmp.$$";

    if (open(my $fh, ">:encoding(UTF-8)", $temp_file)) {
        print $fh encode_json(\@cache);
        close $fh;

        rename($temp_file, $PLANTS_CACHE_FILE)
            or logger::warning("Pflanzen-Cache konnte nicht ersetzt werden: $!");
    }
    else {
        logger::warning("Pflanzen-Cache konnte nicht geschrieben werden: $!");
    }
}

sub load_plants_cache
{
    return undef unless -f $PLANTS_CACHE_FILE;

    open(my $fh, "<", $PLANTS_CACHE_FILE)
        or return undef;

    local $/;
    my $content = <$fh>;
    close $fh;

    my $plants;
    eval { $plants = decode_json($content); };

    if ($@ || ref($plants) ne "ARRAY") {
        logger::warning("Pflanzen-Cache ist ungültig");
        return undef;
    }

    return $plants;
}

sub write_status
{
    my ($status) = @_;

    ensure_data_dir();

    my $temp_file = "$STATUS_FILE.tmp.$$";

    open(my $fh, ">:encoding(UTF-8)", $temp_file)
        or do {
            logger::error("Statusdatei kann nicht geschrieben werden: $!");
            return;
        };

    foreach my $key (sort keys %{$status}) {
        my $value = defined $status->{$key} ? $status->{$key} : "";
        $value =~ s/\r//g;
        $value =~ s/\n/ /g;
        print $fh "$key=$value\n";
    }

    close $fh;

    rename($temp_file, $STATUS_FILE)
        or logger::error("Statusdatei kann nicht ersetzt werden: $!");
}

sub read_key_value_file
{
    my ($file) = @_;
    my %values;

    return \%values unless -f $file;
    open(my $fh, "<:encoding(UTF-8)", $file) or return \%values;

    while (my $line = <$fh>) {
        chomp $line;
        $line =~ s/\r//g;
        next if $line =~ /^\s*$/;
        next if $line =~ /^\s*[#;]/;

        if ($line =~ /^\s*([^=]+?)\s*=\s*(.*?)\s*$/) {
            $values{$1} = $2;
        }
    }

    close $fh;
    return \%values;
}

sub ensure_data_dir
{
    return if -d $DATA_DIR;
    make_path($DATA_DIR, { mode => 0750 });
}

sub normalize
{
    my ($name) = @_;

    $name = "" unless defined $name;
    $name =~ s/ä/ae/g;
    $name =~ s/ö/oe/g;
    $name =~ s/ü/ue/g;
    $name =~ s/Ä/Ae/g;
    $name =~ s/Ö/Oe/g;
    $name =~ s/Ü/Ue/g;
    $name =~ s/ß/ss/g;
    $name =~ s/\s+/_/g;
    $name =~ s/[^A-Za-z0-9_]//g;

    return length($name) ? $name : "Unbekannt";
}

sub timestamp
{
    my ($epoch) = @_;
    $epoch = time() unless defined $epoch;

    return strftime("%Y-%m-%d %H:%M:%S", localtime($epoch));
}
