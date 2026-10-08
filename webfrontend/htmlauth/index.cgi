#!/usr/bin/perl

use strict;
use warnings;
use utf8;

use POSIX qw(strftime);

use lib "/opt/loxberry/bin/plugins/fyta_connect";

use config;
use auth_store;
use version;

binmode STDOUT, ':encoding(UTF-8)';

my $STATUS_FILE =
    "/opt/loxberry/data/plugins/fyta_connect/status.cfg";

my $LOG_FILE =
    "/opt/loxberry/log/plugins/fyta_connect/fyta_connect.log";

my $SCHEDULER_FILE =
    "/opt/loxberry/system/cron/cron.01min/fyta_connect";

my $plugin_version = eval { LoxBerry::System::pluginversion('fyta_connect') };
$plugin_version = version::plugin_version() unless defined $plugin_version && length $plugin_version;
my $cfg = config::read_config();
$cfg = {} unless $cfg && ref($cfg) eq "HASH";

my $status = read_key_value_file($STATUS_FILE);

my $interval = $cfg->{INTERVAL} // 15;

$interval = 15
    unless $interval =~ /^\d+$/
        && $interval >= 1
        && $interval <= 1440;

my $udp_enabled =
    ($cfg->{UDP_ENABLED} // "false") eq "true";

my $udp_host = $cfg->{UDP_HOST} // "";
my $udp_port = $cfg->{UDP_PORT} // "";

my $sync_status =
    $status->{STATUS} // "UNKNOWN";

my $last_run =
    $status->{LAST_RUN} // "Noch keine Synchronisation";

my $last_success =
    $status->{LAST_SEND} || "Noch keine erfolgreiche Übertragung";

my $last_success_epoch =
    $status->{LAST_SUCCESS_EPOCH} // "";
my $scheduler_epoch = "/opt/loxberry/data/plugins/fyta_connect/last_run.timestamp";
my $last_scheduled = 0;
if (open my $sfh, "<", $scheduler_epoch) {
    my $raw = <$sfh>; close $sfh;
    $last_scheduled = $raw if defined $raw && $raw =~ /^\d+$/;
}

my $plants =
    $status->{PLANTS} // 0;

my $telegrams =
    $status->{TELEGRAMS} // 0;

my $errors =
    $status->{ERRORS} // 0;

my $invalid_values =
    $status->{INVALID_VALUES} // 0;

my $duration =
    $status->{DURATION_SECONDS} // 0;

my $message =
    $status->{MESSAGE} // "Noch keine Statusmeldung vorhanden.";

my $next_sync = "Noch nicht berechenbar";

if (
    ($last_scheduled > 0 || (defined $last_success_epoch && $last_success_epoch =~ /^\d+$/ && $last_success_epoch > 0))
) {
    my $next_epoch =
        $last_scheduled > 0 ? $last_scheduled + ($interval * 60) : $last_success_epoch + ($interval * 60);

    $next_sync = strftime(
        "%Y-%m-%d %H:%M:%S",
        localtime($next_epoch)
    );
}

my $scheduler_active =
    -f $SCHEDULER_FILE && -x $SCHEDULER_FILE;

my $log_size = 0;

if (-f $LOG_FILE) {
    $log_size = -s $LOG_FILE;
}

my $log_size_text = format_bytes($log_size);

my $status_class =
    $sync_status eq "OK"
    ? "status-ok"
    : $sync_status eq "ERROR"
        ? "status-error"
        : $sync_status eq "WARNING"
            ? "status-unknown"
            : "status-unknown";

my $status_text =
    $sync_status eq "OK"
    ? "Synchronisation erfolgreich"
    : $sync_status eq "ERROR"
        ? "Synchronisation fehlgeschlagen"
        : $sync_status eq "WARNING"
            ? "Synchronisation mit Ersatzwerten"
            : "Noch kein Status vorhanden";

my $scheduler_class =
    $scheduler_active
    ? "indicator-ok"
    : "indicator-error";

my $scheduler_text =
    $scheduler_active
    ? "Scheduler aktiv"
    : "Scheduler nicht gefunden";

my $udp_class =
    $udp_enabled
    ? "indicator-ok"
    : "indicator-warning";

my $udp_text =
    $udp_enabled
    ? "UDP aktiviert"
    : "UDP deaktiviert";

my $plugin_enabled = ($cfg->{PLUGIN_ENABLED} // "true") eq "true";
my $auth = auth_store::load_auth();
my $token_present = (length($auth->{access_token} // "") || length($cfg->{FYTA_TOKEN} // "")) ? 1 : 0;
my $auto_login = length($cfg->{FYTA_EMAIL} // ($auth->{email} // "")) && auth_store::has_password() ? 1 : 0;
my $miniserver_present = length($udp_host) ? 1 : 0;
my $readiness_text = !$plugin_enabled
    ? "Plugin deaktiviert"
    : !$token_present
        ? "Konfiguration unvollständig – keine FYTA-Anmeldung"
        : !$miniserver_present
            ? "Konfiguration unvollständig – kein Miniserver gewählt"
            : "Betriebsbereit";
my $readiness_class = !$plugin_enabled ? "fyta-unknown" : ($token_present && $miniserver_present ? "fyta-ok" : "fyta-error");
my $toggle_label = $plugin_enabled ? "Plugin deaktivieren" : "Plugin aktivieren";
my $toggle_action = $plugin_enabled ? "disable" : "enable";
my $plugin_text = $plugin_enabled ? "Aktiv" : "Deaktiviert";
my $plugin_class = $plugin_enabled ? "fyta-good" : "fyta-warn";
my $token_text = $auto_login ? "Automatische Anmeldung aktiv" : ($token_present ? "Token vorhanden (Kompatibilitätsmodus)" : "Keine Anmeldung");
my $token_class = $token_present ? "fyta-good" : "fyta-bad";

my $safe_status_text   = html_escape($status_text);
my $safe_last_run      = html_escape($last_run);
my $safe_last_success  = html_escape($last_success);
my $safe_next_sync     = html_escape($next_sync);
my $safe_message       = html_escape($message);
my $safe_udp_host      = html_escape($udp_host);
my $safe_udp_port      = html_escape($udp_port);
my $safe_log_size      = html_escape($log_size_text);
my $safe_scheduler     = html_escape($scheduler_text);
my $safe_udp_text      = html_escape($udp_text);
my $safe_plugin_version = html_escape($plugin_version);

require LoxBerry::Web;
use LoxBerry::System;

binmode STDOUT, ':encoding(UTF-8)';

LoxBerry::Web::lbheader("FYTA Connect", "", "");
print <<'FYTA_STATIC';

<style>
.fyta-wrap{max-width:1000px;margin:0 auto;padding:8px 0 24px}.fyta-nav{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 18px}.fyta-nav a,.fyta-btn{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:10px 16px;border-radius:7px;background:#1976d2;color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:none!important;font-family:Arial,Helvetica,sans-serif!important;font-size:15px!important;line-height:1.25!important;font-weight:700!important;letter-spacing:0!important;text-decoration:none!important;border:0!important;box-shadow:none!important;cursor:pointer;white-space:normal;text-align:center;box-sizing:border-box}.fyta-nav a:link,.fyta-nav a:visited,.fyta-nav a:hover,.fyta-nav a:active,.fyta-nav a:focus,.fyta-btn:link,.fyta-btn:visited,.fyta-btn:hover,.fyta-btn:active,.fyta-btn:focus{color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:none!important;text-decoration:none!important}.fyta-btn::-moz-focus-inner{border:0;padding:0}.fyta-nav a:hover,.fyta-btn:hover{background:#125ea8}.fyta-btn-green{background:#2e7d32}.fyta-btn-green:hover{background:#216425}.fyta-btn-grey{background:#546e7a}.fyta-btn-grey:hover{background:#40545d}.fyta-card{background:#fff;border:1px solid #dfe4e8;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:22px;margin-bottom:20px}.fyta-card h2{margin-top:0}.fyta-header-row{display:flex;justify-content:space-between;align-items:flex-start;gap:20px}.fyta-version{padding:6px 10px;background:#eceff1;border-radius:6px;color:#455a64;font-size:13px;font-weight:700;white-space:nowrap}.fyta-banner{padding:15px;margin-bottom:18px;border-radius:8px;font-weight:700}.fyta-ok{color:#1b5e20;background:#e8f5e9;border:1px solid #a5d6a7}.fyta-error{color:#b71c1c;background:#ffebee;border:1px solid #ef9a9a}.fyta-unknown{color:#5d4037;background:#fff8e1;border:1px solid #ffe082}.fyta-indicators{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:20px}.fyta-indicator,.fyta-stat{padding:15px;border-radius:8px;background:#f7f9fa;border:1px solid #e1e6e9}.fyta-small{color:#607d8b;font-size:13px;margin-bottom:6px}.fyta-good{color:#2e7d32;font-weight:700}.fyta-bad{color:#c62828;font-weight:700}.fyta-warn{color:#ef6c00;font-weight:700}.fyta-details,.fyta-form-grid,.fyta-result-grid{display:grid;grid-template-columns:220px 1fr;gap:12px 20px;align-items:center}.fyta-label{color:#607d8b;font-weight:700}.fyta-message{padding:14px;margin-top:20px;background:#f7f9fa;border-left:4px solid #1976d2;border-radius:4px;overflow-wrap:anywhere}.fyta-stats{display:grid;grid-template-columns:repeat(5,1fr);gap:14px}.fyta-stat{text-align:center}.fyta-number{font-size:26px;font-weight:700;color:#1976d2;margin-bottom:5px}.fyta-actions{display:flex;flex-wrap:wrap;gap:12px}.fyta-form-grid input[type=text],.fyta-form-grid input[type=password],.fyta-form-grid input[type=number]{width:100%;padding:11px 12px;border:1px solid #b0bec5;border-radius:6px;box-sizing:border-box}.fyta-help{grid-column:2;color:#78909c;font-size:13px;margin-top:-8px}.fyta-token-row{display:flex;gap:8px}.fyta-token-row input{flex:1}.fyta-switch{display:flex;align-items:center;gap:10px}.fyta-switch input{width:20px;height:20px}.fyta-pre{overflow:auto;padding:16px;background:#17212b;color:#e5edf3;border-radius:7px;white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.45}.fyta-code{padding:3px 7px;background:#e8edf0;border-radius:4px}.fyta-error-list{margin:12px 0 0 20px}.fyta-footer{text-align:center;color:#78909c;font-size:13px;margin-top:20px}
@media(max-width:760px){.fyta-header-row{flex-direction:column}.fyta-indicators,.fyta-stats{grid-template-columns:1fr 1fr}.fyta-details,.fyta-form-grid,.fyta-result-grid{grid-template-columns:1fr;gap:6px}.fyta-help{grid-column:1;margin-top:0;margin-bottom:8px}.fyta-token-row{flex-direction:column}.fyta-btn,.fyta-nav a{width:100%;text-align:center;box-sizing:border-box}}
@media(max-width:480px){.fyta-indicators,.fyta-stats{grid-template-columns:1fr}}

@media(max-width:760px){
  .fyta-wrap{width:100%;max-width:100%;padding:4px 8px 20px;box-sizing:border-box;overflow-x:hidden}
  .fyta-card{padding:15px 12px;margin-bottom:14px;box-sizing:border-box;overflow:hidden}
  .fyta-card h2{font-size:20px;line-height:1.25;overflow-wrap:anywhere}
  .fyta-header-row{gap:8px}
  .fyta-version{white-space:normal;max-width:100%;box-sizing:border-box}
  .fyta-nav,.fyta-actions{display:grid;grid-template-columns:1fr;gap:8px;width:100%;margin-bottom:12px}
  .fyta-nav a,.fyta-btn{width:100%;max-width:100%;min-height:44px;padding:10px 12px;box-sizing:border-box;white-space:normal;overflow-wrap:anywhere}
  .fyta-indicators,.fyta-stats{grid-template-columns:1fr;gap:9px}
  .fyta-indicator,.fyta-stat{padding:12px;min-width:0;box-sizing:border-box;overflow-wrap:anywhere;word-break:break-word}
  .fyta-details,.fyta-form-grid,.fyta-result-grid{grid-template-columns:minmax(0,1fr);gap:4px}
  .fyta-details .fyta-label{margin-top:8px}
  .fyta-message,.fyta-banner{padding:12px;overflow-wrap:anywhere;word-break:break-word}
  .fyta-pre{font-size:12px;padding:11px;max-width:100%;box-sizing:border-box;white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word}
  .fyta-code{max-width:100%;white-space:normal;overflow-wrap:anywhere;word-break:break-word}
}
@media(max-width:420px){.fyta-wrap{padding-left:5px;padding-right:5px}.fyta-card{padding:13px 10px}.fyta-number{font-size:23px}}

/* Button-Kontrast gegen geerbte LoxBerry-/Browser-Styles absichern */
.fyta-nav a,.fyta-btn,.fyta-nav a:link,.fyta-nav a:visited,.fyta-btn:link,.fyta-btn:visited{color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:none!important;text-decoration:none!important;opacity:1!important}
.fyta-nav a:hover,.fyta-nav a:focus,.fyta-nav a:active,.fyta-btn:hover,.fyta-btn:focus,.fyta-btn:active{color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:none!important;text-decoration:none!important}
.fyta-nav a:focus,.fyta-btn:focus{outline:3px solid rgba(11,92,173,.30)!important;outline-offset:2px!important}
.fyta-btn:disabled,.fyta-btn[disabled],.fyta-nav a[aria-disabled="true"]{background:#6f7f87!important;border-color:#5d6b72!important;color:#fff!important;-webkit-text-fill-color:#fff!important;opacity:.72!important;cursor:not-allowed!important}
</style>
<div class="fyta-wrap"><nav class="fyta-nav"><a href="index.cgi">Startseite</a><a href="settings.cgi">Einstellungen</a><a href="sync.cgi">Jetzt synchronisieren</a></nav>
FYTA_STATIC
print <<"FYTA_HTML";
<section class="fyta-card"><div class="fyta-header-row"><div><h2>FYTA Connect</h2><p>FYTA-Pflanzensensoren automatisch auslesen und Messwerte per UDP an Loxone übertragen.</p></div><div class="fyta-version">Version $safe_plugin_version</div></div></section>
<section class="fyta-card"><h2>Pluginstatus</h2><div class="fyta-banner $readiness_class">$readiness_text</div><div class="fyta-indicators"><div class="fyta-indicator"><div class="fyta-small">Plugin</div><div class="$plugin_class">$plugin_text</div></div><div class="fyta-indicator"><div class="fyta-small">FYTA-Anmeldung</div><div class="$token_class">$token_text</div></div><div class="fyta-indicator"><div class="fyta-small">Miniserver</div><div class="fyta-indicator-value">$safe_udp_host</div></div></div><form method="post" action="toggle.cgi"><input type="hidden" name="action" value="$toggle_action"><button class="fyta-btn fyta-btn-grey" type="submit">$toggle_label</button></form></section>
<section class="fyta-card"><h2>Systemstatus</h2><div class="fyta-banner $status_class">$safe_status_text</div>
<div class="fyta-indicators"><div class="fyta-indicator"><div class="fyta-small">Scheduler</div><div class="$scheduler_class">$safe_scheduler</div></div><div class="fyta-indicator"><div class="fyta-small">UDP</div><div class="$udp_class">$safe_udp_text</div></div><div class="fyta-indicator"><div class="fyta-small">Logdatei</div><strong>$safe_log_size</strong></div></div>
<div class="fyta-details"><div class="fyta-label">Letzter Lauf</div><div>$safe_last_run</div><div class="fyta-label">Zuletzt erfolgreich gesendet</div><div>$safe_last_success</div><div class="fyta-label">Nächste Synchronisation</div><div>$safe_next_sync</div><div class="fyta-label">Intervall</div><div>$interval Minuten</div><div class="fyta-label">UDP-Ziel</div><div>$safe_udp_host:$safe_udp_port</div></div><div class="fyta-message"><strong>Letzte Meldung:</strong><br>$safe_message</div></section>
<section class="fyta-card"><h2>Letzte Synchronisation</h2><div class="fyta-stats"><div class="fyta-stat"><div class="fyta-number">$plants</div><div class="fyta-small">Pflanzen</div></div><div class="fyta-stat"><div class="fyta-number">$telegrams</div><div class="fyta-small">UDP-Telegramme</div></div><div class="fyta-stat"><div class="fyta-number">$invalid_values</div><div class="fyta-small">Ersatzwerte (-9999)</div></div><div class="fyta-stat"><div class="fyta-number">$errors</div><div class="fyta-small">Fehler</div></div><div class="fyta-stat"><div class="fyta-number">${duration}s</div><div class="fyta-small">Dauer</div></div></div></section>
<section class="fyta-card"><h2>Aktionen</h2><div class="fyta-actions"><a class="fyta-btn fyta-btn-green" href="sync.cgi">Jetzt synchronisieren</a><a class="fyta-btn fyta-btn-grey" href="settings.cgi">Einstellungen</a></div></section>
FYTA_HTML
print <<'FYTA_STATIC';
<div class="fyta-footer">FYTA Connect für LoxBerry</div></div>
FYTA_STATIC
LoxBerry::Web::lbfooter();
exit 0;

sub read_key_value_file
{
    my ($file) = @_;

    my %values;

    return \%values unless -f $file;

    open(my $fh, "<:encoding(UTF-8)", $file)
        or return \%values;

    while (my $line = <$fh>) {
        chomp $line;
        $line =~ s/\r//g;

        next if $line =~ /^\s*$/;
        next if $line =~ /^\s*#/;
        next if $line =~ /^\s*;/;

        if ($line =~ /^\s*([^=]+?)\s*=\s*(.*?)\s*$/) {
            $values{$1} = $2;
        }
    }

    close $fh;

    return \%values;
}

sub format_bytes
{
    my ($bytes) = @_;

    $bytes = 0
        unless defined $bytes && $bytes =~ /^\d+$/;

    if ($bytes >= 1024 * 1024) {
        return sprintf(
            "%.2f MB",
            $bytes / (1024 * 1024)
        );
    }

    if ($bytes >= 1024) {
        return sprintf(
            "%.1f kB",
            $bytes / 1024
        );
    }

    return "$bytes Bytes";
}

sub html_escape
{
    my ($text) = @_;

    $text = "" unless defined $text;

    $text =~ s/&/&amp;/g;
    $text =~ s/</&lt;/g;
    $text =~ s/>/&gt;/g;
    $text =~ s/"/&quot;/g;
    $text =~ s/'/&#39;/g;

    return $text;
}