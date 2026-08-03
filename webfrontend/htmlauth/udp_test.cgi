#!/usr/bin/perl

use strict;
use warnings;
use utf8;

use CGI;

use lib "/opt/loxberry/bin/plugins/fyta_connect";

use config;
use udp;

binmode STDOUT, ':encoding(UTF-8)';

my $cgi = CGI->new();
my $cfg = config::read_config();

my $success = 0;
my $host    = "";
my $port    = "";
my $message = "FYTA_Test=1";
my $result  = "";

if (!$cfg || ref($cfg) ne "HASH") {
    $result = "Die Konfiguration konnte nicht gelesen werden.";
}
else {
    my $enabled = $cfg->{UDP_ENABLED} // "false";

    $host = $cfg->{UDP_HOST} // "";
    $port = $cfg->{UDP_PORT} // "";

    if ($enabled ne "true") {
        $result = "UDP ist in den Einstellungen deaktiviert.";
    }
    elsif ($host eq "") {
        $result = "Die UDP-Zieladresse fehlt.";
    }
    elsif (
        $port !~ /^\d+$/
        || $port < 1
        || $port > 65535
    ) {
        $result = "Der konfigurierte UDP-Port ist ungültig.";
    }
    else {
        my $udp_result = udp::send_udp(
            $host,
            $port,
            $message
        );

        if (
            defined $udp_result
            && $udp_result =~ /^OK\b/i
        ) {
            $success = 1;
            $result = $udp_result;
        }
        else {
            $result =
                defined $udp_result && length $udp_result
                ? $udp_result
                : "Das UDP-Modul hat keine Rückmeldung geliefert.";
        }
    }
}

my $safe_host    = html_escape($host);
my $safe_port    = html_escape($port);
my $safe_message = html_escape($message);
my $safe_result  = html_escape($result);

my $status_class = $success ? "success" : "error";
my $status_title = $success
    ? "UDP-Test erfolgreich"
    : "UDP-Test fehlgeschlagen";

require LoxBerry::Web;
use LoxBerry::System;

binmode STDOUT, ':encoding(UTF-8)';

LoxBerry::Web::lbheader("FYTA Connect – UDP-Test", "", "");
print <<'FYTA_STATIC';

<style>
.fyta-wrap{max-width:1000px;margin:0 auto;padding:8px 0 24px}.fyta-nav{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 18px}.fyta-nav a,.fyta-btn{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:10px 16px;border-radius:7px;background:#1976d2;color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:none!important;font-family:Arial,Helvetica,sans-serif!important;font-size:15px!important;line-height:1.25!important;font-weight:700!important;letter-spacing:0!important;text-decoration:none!important;border:0!important;box-shadow:none!important;cursor:pointer;white-space:normal;text-align:center;box-sizing:border-box}.fyta-nav a:link,.fyta-nav a:visited,.fyta-nav a:hover,.fyta-nav a:active,.fyta-nav a:focus,.fyta-btn:link,.fyta-btn:visited,.fyta-btn:hover,.fyta-btn:active,.fyta-btn:focus{color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:none!important;text-decoration:none!important}.fyta-btn::-moz-focus-inner{border:0;padding:0}.fyta-nav a:hover,.fyta-btn:hover{background:#125ea8}.fyta-btn-green{background:#2e7d32}.fyta-btn-green:hover{background:#216425}.fyta-btn-grey{background:#546e7a}.fyta-btn-grey:hover{background:#40545d}.fyta-card{background:#fff;border:1px solid #dfe4e8;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:22px;margin-bottom:20px}.fyta-card h2{margin-top:0}.fyta-header-row{display:flex;justify-content:space-between;align-items:flex-start;gap:20px}.fyta-version{padding:6px 10px;background:#eceff1;border-radius:6px;color:#455a64;font-size:13px;font-weight:700;white-space:nowrap}.fyta-banner{padding:15px;margin-bottom:18px;border-radius:8px;font-weight:700}.fyta-ok{color:#1b5e20;background:#e8f5e9;border:1px solid #a5d6a7}.fyta-error{color:#b71c1c;background:#ffebee;border:1px solid #ef9a9a}.fyta-unknown{color:#5d4037;background:#fff8e1;border:1px solid #ffe082}.fyta-indicators{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:20px}.fyta-indicator,.fyta-stat{padding:15px;border-radius:8px;background:#f7f9fa;border:1px solid #e1e6e9}.fyta-small{color:#607d8b;font-size:13px;margin-bottom:6px}.fyta-good{color:#2e7d32;font-weight:700}.fyta-bad{color:#c62828;font-weight:700}.fyta-warn{color:#ef6c00;font-weight:700}.fyta-details,.fyta-form-grid,.fyta-result-grid{display:grid;grid-template-columns:220px 1fr;gap:12px 20px;align-items:center}.fyta-label{color:#607d8b;font-weight:700}.fyta-message{padding:14px;margin-top:20px;background:#f7f9fa;border-left:4px solid #1976d2;border-radius:4px;overflow-wrap:anywhere}.fyta-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.fyta-stat{text-align:center}.fyta-number{font-size:26px;font-weight:700;color:#1976d2;margin-bottom:5px}.fyta-actions{display:flex;flex-wrap:wrap;gap:12px}.fyta-form-grid input[type=text],.fyta-form-grid input[type=password],.fyta-form-grid input[type=number]{width:100%;padding:11px 12px;border:1px solid #b0bec5;border-radius:6px;box-sizing:border-box}.fyta-help{grid-column:2;color:#78909c;font-size:13px;margin-top:-8px}.fyta-token-row{display:flex;gap:8px}.fyta-token-row input{flex:1}.fyta-switch{display:flex;align-items:center;gap:10px}.fyta-switch input{width:20px;height:20px}.fyta-pre{overflow:auto;padding:16px;background:#17212b;color:#e5edf3;border-radius:7px;white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.45}.fyta-code{padding:3px 7px;background:#e8edf0;border-radius:4px}.fyta-error-list{margin:12px 0 0 20px}.fyta-footer{text-align:center;color:#78909c;font-size:13px;margin-top:20px}
@media(max-width:760px){.fyta-header-row{flex-direction:column}.fyta-indicators,.fyta-stats{grid-template-columns:1fr 1fr}.fyta-details,.fyta-form-grid,.fyta-result-grid{grid-template-columns:1fr;gap:6px}.fyta-help{grid-column:1;margin-top:0;margin-bottom:8px}.fyta-token-row{flex-direction:column}.fyta-btn,.fyta-nav a{width:100%;text-align:center;box-sizing:border-box}}
@media(max-width:480px){.fyta-indicators,.fyta-stats{grid-template-columns:1fr}}
</style>
<div class="fyta-wrap"><nav class="fyta-nav"><a href="index.cgi">Startseite</a><a href="settings.cgi">Einstellungen</a><a href="sync.cgi">Jetzt synchronisieren</a><a href="udp_test.cgi">UDP-Test</a></nav>
FYTA_STATIC
print <<"FYTA_HTML";
<section class="fyta-card"><h2>UDP-Test</h2><p>Testet den direkten UDP-Versand an das konfigurierte Ziel.</p><div class="fyta-banner $status_class"><h3>$status_title</h3></div><div class="fyta-result-grid"><div class="fyta-label">Ziel</div><div>$safe_host:$safe_port</div><div class="fyta-label">Nachricht</div><div><span class="fyta-code">$safe_message</span></div><div class="fyta-label">Ergebnis</div><div>$safe_result</div></div><div class="fyta-actions" style="margin-top:20px"><a class="fyta-btn" href="udp_test.cgi">Test wiederholen</a><a class="fyta-btn fyta-btn-grey" href="settings.cgi">Zu den Einstellungen</a><a class="fyta-btn fyta-btn-grey" href="index.cgi">Zur Startseite</a></div></section>
FYTA_HTML
print <<'FYTA_STATIC';
<div class="fyta-footer">FYTA Connect für LoxBerry</div></div>
FYTA_STATIC
LoxBerry::Web::lbfooter();
exit($success ? 0 : 1);

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