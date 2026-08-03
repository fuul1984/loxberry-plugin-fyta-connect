#!/usr/bin/perl

use strict;
use warnings;
use utf8;

use POSIX qw(strftime);
use File::Path qw(make_path);
use JSON qw(encode_json decode_json);

use lib "/opt/loxberry/bin/plugins/fyta_connect";

use config;
use fyta_api;
use logger;
use udp;

my $INVALID_VALUE = -9999;

my $DATA_DIR = "/opt/loxberry/data/plugins/fyta_connect";
my $STATUS_FILE = "$DATA_DIR/status.cfg";
my $PLANTS_CACHE_FILE = "$DATA_DIR/plants_cache.json";

my $start_epoch = time();
my $plant_count = 0;
my $telegram_count = 0;
my $invalid_value_count = 0;
my $error_count = 0;
my $used_plant_cache = 0;
my $last_error = "";

logger::info("FYTA Connect gestartet");

my $previous_status = read_key_value_file($STATUS_FILE);
my $cfg = config::read_config();

unless ($cfg && ref($cfg) eq "HASH") {
    finish_with_error("Konfiguration konnte nicht gelesen werden");
}

my $token = $cfg->{FYTA_TOKEN} // "";
my $host = $cfg->{UDP_HOST} // "";
my $port = $cfg->{UDP_PORT} // "";
my $udp_enabled = ($cfg->{UDP_ENABLED} // "false") eq "true";

unless (length $token) {
    finish_with_error("Kein FYTA-Token gespeichert");
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
    my $name = normalize($plant_name);

    my %values;

    if ($data && ref($data) eq "HASH") {
        $name = normalize($data->{name} // $plant_name);
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
    }

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

sub finish_with_error
{
    my ($message) = @_;
    my $now = time();

    logger::error($message);

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

    if (open(my $fh, ">", $temp_file)) {
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

    open(my $fh, ">", $temp_file)
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
    open(my $fh, "<", $file) or return \%values;

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
