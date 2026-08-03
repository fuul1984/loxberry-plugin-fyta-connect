#!/usr/bin/perl

use strict;
use warnings;
use utf8;

use CGI;

use lib "/opt/loxberry/bin/plugins/fyta_connect";

use config;

binmode STDOUT, ':encoding(UTF-8)';

my $cgi = CGI->new();
my $cfg = config::read_config();

$cfg = {} unless $cfg && ref($cfg) eq "HASH";

my $fyta_token  = html_escape($cfg->{FYTA_TOKEN}  // "");
my $udp_host    = html_escape($cfg->{UDP_HOST}    // "");
my $udp_port    = html_escape($cfg->{UDP_PORT}    // "5007");
my $interval    = html_escape($cfg->{INTERVAL}    // "15");
my $udp_enabled = ($cfg->{UDP_ENABLED} // "false") eq "true"
    ? "checked"
    : "";

require LoxBerry::Web;
use LoxBerry::System;

binmode STDOUT, ':encoding(UTF-8)';

LoxBerry::Web::lbheader("FYTA Connect – Einstellungen", "", "");
print <<'FYTA_STATIC';

<style>
.fyta-wrap{max-width:1000px;margin:0 auto;padding:8px 0 24px}.fyta-nav{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 18px}.fyta-nav a,.fyta-btn{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:10px 16px;border-radius:7px;background:#1976d2;color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:none!important;font-family:Arial,Helvetica,sans-serif!important;font-size:15px!important;line-height:1.25!important;font-weight:700!important;letter-spacing:0!important;text-decoration:none!important;border:0!important;box-shadow:none!important;cursor:pointer;white-space:normal;text-align:center;box-sizing:border-box}.fyta-nav a:link,.fyta-nav a:visited,.fyta-nav a:hover,.fyta-nav a:active,.fyta-nav a:focus,.fyta-btn:link,.fyta-btn:visited,.fyta-btn:hover,.fyta-btn:active,.fyta-btn:focus{color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:none!important;text-decoration:none!important}.fyta-btn::-moz-focus-inner{border:0;padding:0}.fyta-nav a:hover,.fyta-btn:hover{background:#125ea8}.fyta-btn-green{background:#2e7d32}.fyta-btn-green:hover{background:#216425}.fyta-btn-grey{background:#546e7a}.fyta-btn-grey:hover{background:#40545d}.fyta-card{background:#fff;border:1px solid #dfe4e8;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:22px;margin-bottom:20px}.fyta-card h2{margin-top:0}.fyta-header-row{display:flex;justify-content:space-between;align-items:flex-start;gap:20px}.fyta-version{padding:6px 10px;background:#eceff1;border-radius:6px;color:#455a64;font-size:13px;font-weight:700;white-space:nowrap}.fyta-banner{padding:15px;margin-bottom:18px;border-radius:8px;font-weight:700}.fyta-ok{color:#1b5e20;background:#e8f5e9;border:1px solid #a5d6a7}.fyta-error{color:#b71c1c;background:#ffebee;border:1px solid #ef9a9a}.fyta-unknown{color:#5d4037;background:#fff8e1;border:1px solid #ffe082}.fyta-indicators{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:20px}.fyta-indicator,.fyta-stat{padding:15px;border-radius:8px;background:#f7f9fa;border:1px solid #e1e6e9}.fyta-small{color:#607d8b;font-size:13px;margin-bottom:6px}.fyta-good{color:#2e7d32;font-weight:700}.fyta-bad{color:#c62828;font-weight:700}.fyta-warn{color:#ef6c00;font-weight:700}.fyta-details,.fyta-form-grid,.fyta-result-grid{display:grid;grid-template-columns:220px 1fr;gap:12px 20px;align-items:center}.fyta-label{color:#607d8b;font-weight:700}.fyta-message{padding:14px;margin-top:20px;background:#f7f9fa;border-left:4px solid #1976d2;border-radius:4px;overflow-wrap:anywhere}.fyta-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.fyta-stat{text-align:center}.fyta-number{font-size:26px;font-weight:700;color:#1976d2;margin-bottom:5px}.fyta-actions{display:flex;flex-wrap:wrap;gap:12px}.fyta-form-grid input[type=text],.fyta-form-grid input[type=password],.fyta-form-grid input[type=number]{width:100%;padding:11px 12px;border:1px solid #b0bec5;border-radius:6px;box-sizing:border-box}.fyta-help{grid-column:2;color:#78909c;font-size:13px;margin-top:-8px}.fyta-token-row{display:flex;gap:8px}.fyta-token-row input{flex:1}.fyta-switch{display:flex;align-items:center;gap:10px}.fyta-switch input{width:20px;height:20px}.fyta-pre{overflow:auto;padding:16px;background:#17212b;color:#e5edf3;border-radius:7px;white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.45}.fyta-code{padding:3px 7px;background:#e8edf0;border-radius:4px}.fyta-error-list{margin:12px 0 0 20px}.fyta-footer{text-align:center;color:#78909c;font-size:13px;margin-top:20px}

button.fyta-btn,
input.fyta-btn,
button.fyta-btn:link,
button.fyta-btn:visited {
    appearance: none !important;
    -webkit-appearance: none !important;
    background-image: none !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
}

button.fyta-btn-green,
button.fyta-btn-green:link,
button.fyta-btn-green:visited {
    background-color: #2e7d32 !important;
    border: 1px solid #2e7d32 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

button.fyta-btn-green:hover,
button.fyta-btn-green:focus {
    background-color: #216425 !important;
    border-color: #216425 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

button.fyta-btn-green:active {
    background-color: #174b1b !important;
    border-color: #174b1b !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

@media(max-width:760px){.fyta-header-row{flex-direction:column}.fyta-indicators,.fyta-stats{grid-template-columns:1fr 1fr}.fyta-details,.fyta-form-grid,.fyta-result-grid{grid-template-columns:1fr;gap:6px}.fyta-help{grid-column:1;margin-top:0;margin-bottom:8px}.fyta-token-row{flex-direction:column}.fyta-btn,.fyta-nav a{width:100%;text-align:center;box-sizing:border-box}}
@media(max-width:480px){.fyta-indicators,.fyta-stats{grid-template-columns:1fr}}
</style>
<div class="fyta-wrap"><nav class="fyta-nav"><a href="index.cgi">Startseite</a><a href="settings.cgi">Einstellungen</a><a href="sync.cgi">Jetzt synchronisieren</a><a href="udp_test.cgi">UDP-Test</a></nav>
FYTA_STATIC
print <<"FYTA_HTML";
<section class="fyta-card"><h2>FYTA Connect – Einstellungen</h2><p>Hier konfigurierst du den FYTA-Zugang sowie das UDP-Ziel für die Übertragung an Loxone.</p></section>
<form method="post" action="save.cgi"><section class="fyta-card"><h2>FYTA API</h2><div class="fyta-form-grid"><label for="token">API-Token</label><div class="fyta-token-row"><input id="token" type="password" name="token" value="$fyta_token" autocomplete="off"><button class="fyta-btn fyta-btn-grey" id="toggle-token" type="button" onclick="toggleToken()">Anzeigen</button></div><div class="fyta-help">Der Token wird für den Zugriff auf deine Pflanzen und Messwerte verwendet.</div></div></section>
<section class="fyta-card"><h2>UDP-Ausgabe</h2><div class="fyta-form-grid"><label for="udp_enabled">UDP aktivieren</label><div class="fyta-switch"><input id="udp_enabled" type="checkbox" name="udp_enabled" $udp_enabled><span>Messwerte per UDP senden</span></div><label for="udp_host">Zieladresse</label><input id="udp_host" type="text" name="udp_host" value="$udp_host" placeholder="192.168.x.x" required><div class="fyta-help">IP-Adresse oder Hostname des Loxone Miniservers.</div><label for="udp_port">UDP-Port</label><input id="udp_port" type="number" name="udp_port" value="$udp_port" min="1" max="65535" required><div class="fyta-help">Muss mit dem in Loxone konfigurierten UDP-Port übereinstimmen.</div></div></section>
<section class="fyta-card"><h2>Synchronisation</h2><div class="fyta-form-grid"><label for="interval">Abrufintervall</label><input id="interval" type="number" name="interval" value="$interval" min="1" max="1440" required><div class="fyta-help">Intervall in Minuten. Der LoxBerry-Minutenjob übernimmt Änderungen automatisch.</div></div></section>
<section class="fyta-card"><div class="fyta-actions"><button class="fyta-btn fyta-btn-green" type="submit">Einstellungen speichern</button><a class="fyta-btn" href="udp_test.cgi">UDP testen</a><a class="fyta-btn fyta-btn-grey" href="index.cgi">Abbrechen</a></div></section></form>
<script>function toggleToken(){const i=document.getElementById('token');const b=document.getElementById('toggle-token');if(i.type==='password'){i.type='text';b.textContent='Verbergen';}else{i.type='password';b.textContent='Anzeigen';}}</script>
FYTA_HTML
print <<'FYTA_STATIC';
<div class="fyta-footer">FYTA Connect für LoxBerry</div></div>
FYTA_STATIC
LoxBerry::Web::lbfooter();
exit 0;

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