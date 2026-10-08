#!/usr/bin/perl
use strict;
use warnings;
use utf8;
use CGI;
use JSON qw(decode_json);
use lib "/opt/loxberry/bin/plugins/fyta_connect";
use config;
use udp;
use version;
require LoxBerry::Web;
use LoxBerry::System;

binmode STDOUT, ':encoding(UTF-8)';

my $cgi = CGI->new();
my $cfg = config::read_config();
$cfg = {} unless $cfg && ref($cfg) eq 'HASH';
my $plugin_version = eval { LoxBerry::System::pluginversion('fyta_connect') };
$plugin_version = version::plugin_version() unless defined $plugin_version && length $plugin_version;
my $safe_plugin_version = html_escape($plugin_version);

my $is_udp_test = (($cgi->param('action') // '') eq 'udp_test') ? 1 : 0;
my $SENSOR_META_FILE = '/opt/loxberry/data/plugins/fyta_connect/sensor_meta.json';
my $PLANTS_CACHE_FILE = '/opt/loxberry/data/plugins/fyta_connect/plants_cache.json';
my $sensor_meta = load_sensor_meta($SENSOR_META_FILE);
my $plants_cache = load_json_array($PLANTS_CACHE_FILE);
$sensor_meta = merge_current_rows($sensor_meta, $plants_cache);
my @servers = get_servers();

# Für einen UDP-Test werden die aktuell im Formular stehenden Werte verwendet,
# ohne die Konfiguration zu speichern. Damit kann ein geänderter Miniserver/
# Port getestet werden, bevor "Einstellungen speichern" gedrückt wird.
my $view_cfg = { %{$cfg} };
if ($is_udp_test) {
    $view_cfg->{FYTA_EMAIL} = scalar($cgi->param('email') // ($cfg->{FYTA_EMAIL} // ''));
    $view_cfg->{UDP_PORT} = scalar($cgi->param('udp_port') // '5007');
    $view_cfg->{INTERVAL} = scalar($cgi->param('interval') // '15');
    $view_cfg->{MINISERVER_NO} = scalar($cgi->param('miniserver_no') // '');
    $view_cfg->{UDP_ENABLED} = defined($cgi->param('udp_enabled')) ? 'true' : 'false';
    $view_cfg->{UDP_SEND_MODE} = scalar($cgi->param('udp_send_mode') // 'all');

    if (ref($sensor_meta) eq 'ARRAY') {
        for my $item (@{$sensor_meta}) {
            next unless ref($item) eq 'HASH';
            my $id = $item->{config_id} // '';
            next unless $id =~ /^[A-Za-z0-9_]+$/;
            my $hours = $cgi->param("current_hours_$id");
            $view_cfg->{"CURRENT_MAX_AGE_HOURS_$id"} = $hours if defined $hours;
            my $plant_cfg_id = $item->{plant_config_id} // stable_plant_config_id($item->{plant_id});
            $view_cfg->{"SEND_CURRENT_$plant_cfg_id"} = (($cgi->param("send_current_$id") // '0') eq '1') ? 'true' : 'false';
        }
    }
}

my $auth = load_auth_status('/opt/loxberry/data/plugins/fyta_connect/auth.json');
my $email_raw = $view_cfg->{FYTA_EMAIL} // ($auth->{email} // '');
my $email = html_escape($email_raw);
my $password_saved = defined($auth->{password_enc}) && length($auth->{password_enc} // '') ? 1 : 0;
my $token_saved = (length($auth->{access_token} // '') || length($cfg->{FYTA_TOKEN} // '')) ? 1 : 0;
my $password_hint = $password_saved ? 'Passwort ist sicher hinterlegt. Leer lassen, um es unverändert zu behalten.' : 'Passwort einmalig eingeben. Es wird geschützt gespeichert und nicht in fyta.cfg abgelegt.';
my $token_hint = $token_saved ? 'Ein Token ist bereits geschützt gespeichert. Nur ausfüllen, wenn du ihn ersetzen möchtest.' : 'Optional für bestehende Installationen: vorhandenen API-Token übernehmen.';
my $email_status = length($email_raw) ? 'Hinterlegt' : 'Nicht hinterlegt';
my $password_status = $password_saved ? 'Gespeichert' : 'Nicht gespeichert';
my $token_status = $token_saved ? 'Gespeichert' : 'Nicht gespeichert';
my $email_status_class = length($email_raw) ? 'fyta-auth-ok' : 'fyta-auth-missing';
my $password_status_class = $password_saved ? 'fyta-auth-ok' : 'fyta-auth-missing';
my $token_status_class = $token_saved ? 'fyta-auth-ok' : 'fyta-auth-missing';
my $password_placeholder = $password_saved ? 'Passwort gespeichert – nur zum Ändern ausfüllen' : 'FYTA-Passwort eingeben';
my $token_placeholder = $token_saved ? 'Token gespeichert – nur zum Ersetzen ausfüllen' : 'Optional: bestehenden API-Token eingeben';
my $port_raw = $view_cfg->{UDP_PORT} // '5007';
my $interval_raw = $view_cfg->{INTERVAL} // '15';
my $udp_enabled_raw = $view_cfg->{UDP_ENABLED} // 'true';
my $selected_no = $view_cfg->{MINISERVER_NO} // '';
my $current_host = $cfg->{UDP_HOST} // '';

my $port = html_escape($port_raw);
my $interval = html_escape($interval_raw);
my $udp_enabled = $udp_enabled_raw eq 'true' ? 'checked' : '';
my $mode_changes = ($view_cfg->{UDP_SEND_MODE} // 'all') eq 'changes' ? 'selected' : '';
my $mode_all = $mode_changes ? '' : 'selected';

my ($selected_index, $selected_host, $selected_name) = select_server(\@servers, $selected_no, $current_host);
my $options = '';
if (@servers) {
    for my $i (0 .. $#servers) {
        my $ms = $servers[$i];
        my $sel = $i == $selected_index ? ' selected' : '';
        my $label = html_escape($ms->{name});
        my $host = html_escape($ms->{host});
        my $no = html_escape($ms->{no});
        $options .= qq{<option value="$no" data-host="$host"$sel>$label – $host</option>};
    }
} else {
    my $safe = html_escape($current_host);
    $options = qq{<option value="" selected>Kein Miniserver in LoxBerry konfiguriert</option>};
    $options .= qq{<option value="manual">Bisheriges Ziel: $safe</option>} if length $safe;
}

my $udp_test_html = '';
if ($is_udp_test) {
    my ($ok, $result, $test_host, $test_port, $test_message) = run_udp_test(
        \@servers,
        scalar($cgi->param('miniserver_no') // ''),
        scalar($cgi->param('udp_port') // ''),
        $current_host,
    );
    my $class = $ok ? 'fyta-test-ok' : 'fyta-test-error';
    my $title = $ok ? 'UDP-Test erfolgreich' : 'UDP-Test fehlgeschlagen';
    $udp_test_html = qq{<div id="udp-test" class="fyta-test-result $class"><strong>$title</strong><br>Ziel: } . html_escape($test_host) . ':' . html_escape($test_port) . qq{<br>Nachricht: <span class="fyta-code">} . html_escape($test_message) . qq{</span><br>Ergebnis: } . html_escape($result) . qq{</div>};
}

my $sensor_section = build_sensor_section($sensor_meta, $view_cfg);

LoxBerry::Web::lbheader("FYTA Connect – Einstellungen", "", "");
print <<'HTML';
<style>
.fyta-wrap{max-width:1000px;margin:0 auto;padding:8px 0 24px}.fyta-nav,.fyta-actions{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 18px}.fyta-nav a,.fyta-btn{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:10px 16px;border-radius:7px;background:#0b5cad!important;color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:none!important;font-size:15px!important;font-weight:700!important;text-decoration:none!important;border:1px solid #084a8a!important;cursor:pointer}.fyta-btn:hover,.fyta-nav a:hover{background:#084a8a!important}.fyta-btn-green{background:#237a35!important;border-color:#195d27!important}.fyta-btn-green:hover{background:#195d27!important}.fyta-btn-grey{background:#455a64!important;border-color:#34434a!important}.fyta-card{background:#fff;border:1px solid #dfe4e8;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:22px;margin-bottom:20px}.fyta-form-grid{display:grid;grid-template-columns:220px 1fr;gap:12px 20px;align-items:center}.fyta-form-grid input,.fyta-form-grid select{width:100%;padding:11px 12px;border:1px solid #b0bec5;border-radius:6px;box-sizing:border-box;background:#fff}.fyta-help{grid-column:2;color:#78909c;font-size:13px;margin-top:-8px}.fyta-token-row{display:flex;gap:8px}.fyta-token-row input{flex:1}.fyta-switch{display:flex;align-items:center;gap:10px}.fyta-switch input{width:20px;height:20px}.fyta-sensor-table{width:100%;border-collapse:collapse}.fyta-sensor-table th,.fyta-sensor-table td{padding:10px;border-bottom:1px solid #e1e6e9;text-align:left;vertical-align:middle}.fyta-sensor-table th{background:#f7f9fa}.fyta-sensor-table input[type=number]{width:90px;padding:8px}.fyta-current-toggle{display:inline-flex;align-items:center;gap:8px;min-height:34px;padding:6px 10px;border:1px solid #9aa8b0;border-radius:6px;background:#fff;color:#263238;font-weight:600;cursor:pointer;white-space:nowrap;box-shadow:none;text-shadow:none}.fyta-current-toggle:hover{background:#f3f6f7}.fyta-current-toggle:focus{outline:3px solid rgba(11,92,173,.25);outline-offset:2px}.fyta-current-toggle[aria-pressed="true"]{background:#e8f5e9;border-color:#6aa675;color:#1b5e20}.fyta-current-icon{display:inline-block;width:18px;text-align:center;font-size:18px;line-height:1}.fyta-code{font-family:monospace;background:#eef2f4;padding:3px 6px;border-radius:4px}.fyta-auth-status{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:0 0 18px}.fyta-auth-item{padding:10px 12px;background:#f7f9fa;border:1px solid #e1e6e9;border-radius:7px}.fyta-auth-label{display:block;color:#607d8b;font-size:12px;margin-bottom:4px}.fyta-auth-ok{color:#2e7d32;font-weight:700}.fyta-auth-missing{color:#c62828;font-weight:700}.fyta-test-result{margin-top:16px;padding:14px 16px;border-radius:8px;line-height:1.55}.fyta-test-ok{background:#e8f5e9;border:1px solid #a5d6a7;color:#1b5e20}.fyta-test-error{background:#ffebee;border:1px solid #ef9a9a;color:#b71c1c}.fyta-footer{text-align:center;color:#78909c;font-size:13px;margin-top:20px}
@media(max-width:760px){
  .fyta-wrap{width:100%;max-width:100%;padding:4px 8px 20px;box-sizing:border-box;overflow-x:hidden}
  .fyta-card{padding:15px 12px;margin-bottom:14px;border-radius:8px;box-sizing:border-box;overflow:hidden}
  .fyta-card h2{font-size:20px;line-height:1.25;margin:0 0 10px;overflow-wrap:anywhere}
  .fyta-card p{line-height:1.45;overflow-wrap:anywhere}
  .fyta-nav,.fyta-actions{display:grid;grid-template-columns:1fr;gap:8px;width:100%;margin-bottom:12px}
  .fyta-nav a,.fyta-btn{width:100%;max-width:100%;min-height:44px;padding:10px 12px;box-sizing:border-box;white-space:normal;overflow-wrap:anywhere;text-align:center}
  .fyta-auth-status{grid-template-columns:1fr;gap:8px}
  .fyta-form-grid{grid-template-columns:minmax(0,1fr);gap:5px;width:100%}
  .fyta-form-grid>label{font-weight:700;margin-top:8px;overflow-wrap:anywhere}
  .fyta-form-grid input,.fyta-form-grid select{min-width:0;max-width:100%;font-size:16px;min-height:44px}
  .fyta-help{grid-column:1;margin:0 0 7px;line-height:1.4;overflow-wrap:anywhere}
  .fyta-token-row{display:grid;grid-template-columns:minmax(0,1fr);gap:7px;width:100%;min-width:0}
  .fyta-token-row input{min-width:0;width:100%}
  .fyta-switch{align-items:flex-start;line-height:1.4}
  .fyta-sensor-table,.fyta-sensor-table tbody{display:block;width:100%}
  .fyta-sensor-table thead{display:none}
  .fyta-sensor-table tr{display:block;width:100%;margin:0 0 12px;border:1px solid #d7dfe3;border-radius:8px;background:#fff;overflow:hidden;box-sizing:border-box}
  .fyta-sensor-table td{display:grid;grid-template-columns:minmax(105px,40%) minmax(0,60%);gap:8px;align-items:center;width:100%;padding:9px 10px;border-bottom:1px solid #edf0f2;box-sizing:border-box;overflow-wrap:anywhere;word-break:break-word}
  .fyta-sensor-table td:last-child{border-bottom:0}
  .fyta-sensor-table td:before{font-weight:700;color:#607d8b;font-size:12px;line-height:1.25}
  .fyta-sensor-table td:nth-child(1):before{content:'Pflanze'}
  .fyta-sensor-table td:nth-child(2):before{content:'Sensor'}
  .fyta-sensor-table td:nth-child(3):before{content:'Empfehlung'}
  .fyta-sensor-table td:nth-child(4):before{content:'Grenze'}
  .fyta-sensor-table td:nth-child(5):before{content:'Aktuell senden'}
  .fyta-sensor-table td:nth-child(6):before{content:'Loxone'}
  .fyta-sensor-table input[type=number]{width:76px;max-width:100%;font-size:16px;min-height:40px;box-sizing:border-box}
  .fyta-current-toggle{max-width:100%;min-height:40px;white-space:normal;line-height:1.25;justify-content:flex-start;box-sizing:border-box}
  .fyta-code{display:inline-block;max-width:100%;white-space:normal;overflow-wrap:anywhere;word-break:break-word;box-sizing:border-box}
  .fyta-test-result{overflow-wrap:anywhere;word-break:break-word}
}
@media(max-width:420px){
  .fyta-wrap{padding-left:5px;padding-right:5px}
  .fyta-card{padding:13px 10px}
  .fyta-sensor-table td{grid-template-columns:1fr;gap:4px}
  .fyta-sensor-table td:before{display:block}
}

.fyta-current-toggle,.fyta-current-toggle:hover,.fyta-current-toggle:focus,.fyta-current-toggle:active{color:#263238!important;-webkit-text-fill-color:#263238!important;text-shadow:none!important}
.fyta-current-toggle[aria-pressed="true"],.fyta-current-toggle[aria-pressed="true"]:hover,.fyta-current-toggle[aria-pressed="true"]:focus,.fyta-current-toggle[aria-pressed="true"]:active{color:#1b5e20!important;-webkit-text-fill-color:#1b5e20!important;text-shadow:none!important}
/* Button-Kontrast gegen geerbte LoxBerry-/Browser-Styles absichern */
.fyta-nav a,.fyta-btn,.fyta-nav a:link,.fyta-nav a:visited,.fyta-btn:link,.fyta-btn:visited{color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:none!important;text-decoration:none!important;opacity:1!important}
.fyta-nav a:hover,.fyta-nav a:focus,.fyta-nav a:active,.fyta-btn:hover,.fyta-btn:focus,.fyta-btn:active{color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:none!important;text-decoration:none!important}
.fyta-nav a:focus,.fyta-btn:focus{outline:3px solid rgba(11,92,173,.30)!important;outline-offset:2px!important}
.fyta-btn:disabled,.fyta-btn[disabled],.fyta-nav a[aria-disabled="true"]{background:#6f7f87!important;border-color:#5d6b72!important;color:#fff!important;-webkit-text-fill-color:#fff!important;opacity:.72!important;cursor:not-allowed!important}
</style>
<div class="fyta-wrap"><nav class="fyta-nav"><a href="index.cgi">Startseite</a><a href="settings.cgi">Einstellungen</a><a href="sync.cgi">Jetzt synchronisieren</a></nav>
HTML
print qq{
<section class="fyta-card"><h2>FYTA Connect – Einstellungen</h2><p>FYTA-Anmeldung, LoxBerry-Miniserver, UDP-Port und Synchronisationsintervall konfigurieren.</p><p class="fyta-help" style="grid-column:auto;margin:0">Version $safe_plugin_version</p></section>
<form method="post" action="save.cgi">
<section class="fyta-card"><h2>FYTA API / Anmeldung</h2>
<div class="fyta-auth-status">
<div class="fyta-auth-item"><span class="fyta-auth-label">FYTA E-Mail</span><span class="$email_status_class">$email_status</span></div>
<div class="fyta-auth-item"><span class="fyta-auth-label">Passwort</span><span class="$password_status_class">$password_status</span></div>
<div class="fyta-auth-item"><span class="fyta-auth-label">API-Token</span><span class="$token_status_class">$token_status</span></div>
</div>
<div class="fyta-form-grid">
<label for="email">FYTA E-Mail</label><input id="email" type="email" name="email" value="$email" autocomplete="username" placeholder="name\@beispiel.ch"><div class="fyta-help">E-Mail des FYTA-Kontos. Bei einer älteren Installation muss sie gegebenenfalls einmal ergänzt werden, damit die automatische Neuanmeldung möglich ist.</div>
<label for="password">FYTA Passwort</label><div class="fyta-token-row"><input id="password" type="password" name="password" value="" autocomplete="new-password" placeholder="$password_placeholder"></div><div class="fyta-help">$password_hint</div>
<label for="token">Bestehender API-Token</label><div class="fyta-token-row"><input id="token" type="password" name="token" value="" autocomplete="off" placeholder="$token_placeholder"></div><div class="fyta-help">$token_hint Der gespeicherte Token wird aus Sicherheitsgründen niemals angezeigt.</div>
</div></section>
<section class="fyta-card"><h2>UDP-Ausgabe</h2><div class="fyta-form-grid">
<label for="udp_enabled">UDP aktivieren</label><div class="fyta-switch"><input id="udp_enabled" type="checkbox" name="udp_enabled" $udp_enabled><span>Messwerte per UDP senden</span></div>
<label for="miniserver_no">Loxone Miniserver</label><select id="miniserver_no" name="miniserver_no" required>$options</select><div class="fyta-help">Die Liste wird direkt aus Einstellungen → Miniserver im LoxBerry gelesen.</div>
<label for="udp_send_mode">Sendeverhalten</label><select id="udp_send_mode" name="udp_send_mode"><option value="all" $mode_all>Immer alle Werte senden</option><option value="changes" $mode_changes>Nur geänderte Werte senden</option></select><div class="fyta-help">Nach Neustart oder Änderung des UDP-Ziels werden alle Werte einmalig übertragen. Der Heartbeat bleibt unabhängig.</div>
<label for="udp_port">UDP-Port</label><input id="udp_port" type="number" name="udp_port" value="$port" min="1" max="65535" required><div class="fyta-help">Port des virtuellen UDP-Eingangs in Loxone.</div>
</div>
<div class="fyta-actions" style="margin-top:18px"><button class="fyta-btn" type="submit" name="action" value="udp_test" formaction="settings.cgi" formmethod="post">UDP-Verbindung testen</button></div>
$udp_test_html
</section>
<section class="fyta-card"><h2>Synchronisation</h2><div class="fyta-form-grid"><label for="interval">Abrufintervall</label><input id="interval" type="number" name="interval" value="$interval" min="1" max="1440" required><div class="fyta-help">Intervall in Minuten.</div></div></section>
$sensor_section
<section class="fyta-card"><div class="fyta-actions"><button class="fyta-btn fyta-btn-green" type="submit">Einstellungen speichern</button><a class="fyta-btn fyta-btn-grey" href="index.cgi">Abbrechen</a></div></section></form>
<script>function updateCurrentButton(btn,value){const hidden=document.getElementById(btn.dataset.target);hidden.value=value?'1':'0';btn.setAttribute('aria-pressed',value?'true':'false');btn.querySelector('.fyta-current-icon').textContent=value?'☑':'☐';}function toggleCurrent(btn){updateCurrentButton(btn,btn.getAttribute('aria-pressed')!=='true');}function setAllCurrent(value){document.querySelectorAll('.fyta-current-toggle').forEach(function(btn){updateCurrentButton(btn,value);});}</script>
};
print qq{<div class="fyta-footer">FYTA Connect für LoxBerry · Version $safe_plugin_version</div></div>};
LoxBerry::Web::lbfooter();
exit 0;


sub load_auth_status {
    my ($file) = @_;
    return {} unless defined $file && -f $file;
    open(my $fh, '<', $file) or return {};
    local $/;
    my $raw = <$fh>;
    close $fh;
    my $data;
    eval { $data = decode_json($raw // ''); };
    return {} if $@ || ref($data) ne 'HASH';
    return $data;
}

sub select_server {
    my ($servers, $wanted_no, $current_host) = @_;
    return (0, '', '') unless ref($servers) eq 'ARRAY' && @{$servers};

    my $selected_index = 0;
    my $found = 0;
    if (defined $wanted_no && length $wanted_no) {
        for my $i (0 .. $#{$servers}) {
            if (defined $servers->[$i]{no} && "$servers->[$i]{no}" eq "$wanted_no") {
                $selected_index = $i;
                $found = 1;
                last;
            }
        }
    }
    if (!$found && defined $current_host && length $current_host) {
        for my $i (0 .. $#{$servers}) {
            if (lc($servers->[$i]{host} // '') eq lc($current_host)) {
                $selected_index = $i;
                last;
            }
        }
    }
    return ($selected_index, $servers->[$selected_index]{host} // '', $servers->[$selected_index]{name} // '');
}

sub run_udp_test {
    my ($servers, $wanted_no, $wanted_port, $fallback_host) = @_;
    my $message = 'FYTA_Test=1';
    my $host = '';
    my $port = $wanted_port // '';

    if (ref($servers) eq 'ARRAY' && @{$servers}) {
        for my $server (@{$servers}) {
            if (defined $wanted_no && length $wanted_no && "$server->{no}" eq "$wanted_no") {
                $host = $server->{host} // '';
                last;
            }
        }
        $host = $servers->[0]{host} // '' unless length $host;
    } elsif (defined $fallback_host && length $fallback_host) {
        $host = $fallback_host;
    }

    return (0, 'Kein LoxBerry-Miniserver verfügbar.', $host, $port, $message) unless length $host;
    return (0, 'Der UDP-Port muss zwischen 1 und 65535 liegen.', $host, $port, $message)
        unless $port =~ /^\d+$/ && $port >= 1 && $port <= 65535;

    my $udp_result = udp::send_udp($host, $port, $message);
    my $ok = defined($udp_result) && $udp_result =~ /^OK\b/i ? 1 : 0;
    my $result = defined($udp_result) && length($udp_result)
        ? $udp_result
        : 'Das UDP-Modul hat keine Rückmeldung geliefert.';
    return ($ok, $result, $host, $port, $message);
}

sub load_sensor_meta {
    my ($file) = @_;
    return load_json_array($file);
}

sub load_json_array {
    my ($file) = @_;
    return [] unless defined $file && -f $file;
    open(my $fh, '<', $file) or return [];
    local $/;
    my $content = <$fh>;
    close $fh;
    my $data;
    eval { $data = decode_json($content); };
    return [] if $@ || ref($data) ne 'ARRAY';
    return $data;
}

sub merge_current_rows {
    my ($meta, $plants) = @_;
    $meta = [] unless ref($meta) eq 'ARRAY';
    $plants = [] unless ref($plants) eq 'ARRAY';
    my @rows = @{$meta};
    my %known = map { defined($_->{plant_id}) ? ("$_->{plant_id}" => 1) : () } grep { ref($_) eq 'HASH' } @rows;
    for my $plant (@{$plants}) {
        next unless ref($plant) eq 'HASH' && defined $plant->{id};
        next if $known{"$plant->{id}"};
        my $pid = $plant->{id};
        my $pcid = stable_plant_config_id($pid);
        push @rows, {
            plant_id => $pid,
            plant_name => ($plant->{nickname} // $plant->{name} // 'Unbekannt'),
            sensor_id => '',
            sensor_type => 'Noch keine Sensormetadaten',
            config_id => $pcid,
            plant_config_id => $pcid,
            recommended_hours => 6,
        };
    }
    return \@rows;
}

sub build_sensor_section {
    my ($list, $cfg) = @_;
    my $html = '<section class="fyta-card"><h2>Sensor-Aktualität</h2>';
    $html .= '<p>Für jeden erkannten Sensor kann festgelegt werden, nach wie vielen Stunden seine Daten als veraltet gelten. Der vorgeschlagene Standardwert wird automatisch anhand des erkannten FYTA-Sensortyps gesetzt.</p>';

    if (ref($list) ne 'ARRAY' || !@{$list}) {
        $html .= '<div class="fyta-help" style="grid-column:auto">Noch keine Sensordaten erkannt. Bitte zuerst eine Synchronisation ausführen; danach erscheinen die Sensoren hier automatisch.</div></section>';
        return $html;
    }

    $html .= '<div class="fyta-actions"><button class="fyta-btn fyta-btn-green" type="button" onclick="setAllCurrent(true)">Alle Aktuell-Werte aktivieren</button><button class="fyta-btn fyta-btn-grey" type="button" onclick="setAllCurrent(false)">Alle deaktivieren</button></div>';
    $html .= '<table class="fyta-sensor-table"><thead><tr><th>Pflanze</th><th>Sensor</th><th>Empfehlung</th><th>Grenze</th><th>Aktuell senden</th><th>Loxone</th></tr></thead><tbody>';
    for my $item (@{$list}) {
        next unless ref($item) eq 'HASH';
        my $id = $item->{config_id} // '';
        next unless $id =~ /^[A-Za-z0-9_]+$/;
        my $plant = html_escape($item->{plant_name} // 'Unbekannt');
        my $type_text = $item->{sensor_type} // 'Unbekannt';
        if (($type_text eq 'Unbekannt' || $type_text =~ /^FYTA /) && defined $item->{sensor_type_id} && length($item->{sensor_type_id})) {
            $type_text = 'FYTA Typ ' . $item->{sensor_type_id};
        }
        if (defined $item->{sensor_version} && length($item->{sensor_version})) {
            $type_text .= ' · FW ' . $item->{sensor_version};
        }
        my $type = html_escape($type_text);
        my $recommend = $item->{recommended_hours} // 6;
        $recommend = 6 unless $recommend =~ /^\d+(?:\.\d+)?$/;
        my $hours_key = "CURRENT_MAX_AGE_HOURS_$id";
        my $plant_cfg_id = $item->{plant_config_id} // stable_plant_config_id($item->{plant_id});
        my $send_key = "SEND_CURRENT_$plant_cfg_id";
        my $legacy_send_key = "SEND_CURRENT_$id";
        my $hours = $cfg->{$hours_key};
        $hours = $recommend unless defined $hours && $hours =~ /^\d+(?:\.\d+)?$/ && $hours > 0;
        my $send_cfg = defined($cfg->{$send_key}) && $cfg->{$send_key} ne ''
            ? $cfg->{$send_key}
            : (defined($cfg->{$legacy_send_key}) && $cfg->{$legacy_send_key} ne '' ? $cfg->{$legacy_send_key} : 'true');
        my $enabled = lc($send_cfg // 'true') =~ /^(?:true|1|yes|on)$/ ? 1 : 0;
        my $send_value = $enabled ? '1' : '0';
        my $pressed = $enabled ? 'true' : 'false';
        my $icon = $enabled ? '☑' : '☐';
        my $normalized = $item->{plant_name} // 'Unbekannt';
        $normalized =~ s/ä/ae/g; $normalized =~ s/ö/oe/g; $normalized =~ s/ü/ue/g;
        $normalized =~ s/Ä/Ae/g; $normalized =~ s/Ö/Oe/g; $normalized =~ s/Ü/Ue/g; $normalized =~ s/ß/ss/g;
        $normalized =~ s/\s+/_/g; $normalized =~ s/[^A-Za-z0-9_]//g;
        $normalized = 'Unbekannt' unless length $normalized;
        my $lox = html_escape('FYTA_' . $normalized . '_Aktuell=\v');
        $html .= qq{<tr><td><strong>$plant</strong></td><td>$type</td><td>${recommend} h</td><td><input type="number" name="current_hours_$id" value="$hours" min="1" max="168" step="1"> h</td><td><input type="hidden" id="send_current_$id" name="send_current_$id" value="$send_value"><button type="button" class="fyta-current-toggle" data-target="send_current_$id" aria-pressed="$pressed" onclick="toggleCurrent(this)"><span class="fyta-current-icon" aria-hidden="true">$icon</span><span>Aktuell senden</span></button></td><td><span class="fyta-code">$lox</span><br><small>Digital: 0/1</small></td></tr>};
    }
    $html .= '</tbody></table><p class="fyta-help" style="grid-column:auto;margin-top:12px">1 = Daten innerhalb der eingestellten Grenze; 0 = Daten älter oder Zeitstempel ungültig. Unbekannte Sensortypen starten mit 6 Stunden.</p></section>';
    return $html;
}

sub stable_plant_config_id {
    my ($plant_id) = @_;
    my $id = 'PLANT_' . (defined $plant_id ? $plant_id : 'UNKNOWN');
    $id =~ s/[^A-Za-z0-9_]/_/g;
    return uc($id);
}

sub get_servers {
    my @raw = eval { LoxBerry::System::get_miniservers() };
    return () if $@;

    my @candidates;
    collect_server_candidates(\@candidates, \@raw);

    my @out;
    my %seen;
    my $fallback_no = 0;

    for my $entry (@candidates) {
        next unless ref($entry) eq 'HASH';

        my $host = first_value(
            $entry,
            qw(IPAddress IPADDRESS Ipaddress ipaddress IP ip HOST Host host HOSTNAME Hostname hostname ADDRESS Address address)
        );
        next unless defined $host && length $host;

        # Keine doppelten Einträge, falls dieselbe Struktur mehrfach traversiert wurde.
        my $host_key = lc($host);
        next if $seen{$host_key}++;

        $fallback_no++;
        my $no = first_value(
            $entry,
            qw(MSNO msno NO no NUMBER number NR nr INDEX index)
        );
        $no = $fallback_no unless defined $no && length $no;

        my $name = first_value(
            $entry,
            qw(NAME Name name MSNAME msname LOCATION Location location FRIENDLYNAME FriendlyName friendlyname)
        );
        $name = "Miniserver $no" unless defined $name && length $name;

        push @out, {
            no   => "$no",
            name => "$name",
            host => "$host",
        };
    }

    return sort {
        ($a->{no} =~ /^\d+$/ && $b->{no} =~ /^\d+$/)
            ? $a->{no} <=> $b->{no}
            : $a->{no} cmp $b->{no}
    } @out;
}

sub collect_server_candidates {
    my ($out, $node, $depth) = @_;
    $depth //= 0;
    return if $depth > 8;

    if (ref($node) eq 'ARRAY') {
        collect_server_candidates($out, $_, $depth + 1) for @{$node};
        return;
    }

    return unless ref($node) eq 'HASH';

    my $host = first_value(
        $node,
        qw(IPAddress IPADDRESS Ipaddress ipaddress IP ip HOST Host host HOSTNAME Hostname hostname ADDRESS Address address)
    );
    push @{$out}, $node if defined $host && length $host;

    for my $value (values %{$node}) {
        collect_server_candidates($out, $value, $depth + 1)
            if ref($value) eq 'HASH' || ref($value) eq 'ARRAY';
    }
}

sub first_value {
    my ($h, @keys) = @_;
    for my $key (@keys) {
        return $h->{$key}
            if exists $h->{$key}
            && defined $h->{$key}
            && length $h->{$key};
    }
    return undef;
}

sub html_escape { my ($t)=@_; $t='' unless defined $t; $t=~s/&/&amp;/g;$t=~s/</&lt;/g;$t=~s/>/&gt;/g;$t=~s/"/&quot;/g;$t=~s/'/&#39;/g; return $t; }
