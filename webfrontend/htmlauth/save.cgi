#!/usr/bin/perl

use strict;
use warnings;
use utf8;

use CGI;

use lib "/opt/loxberry/bin/plugins/fyta_connect";

use config;

binmode STDOUT, ':encoding(UTF-8)';

my $cgi = CGI->new();

my $existing_cfg = config::read_config();
$existing_cfg = {} unless $existing_cfg && ref($existing_cfg) eq "HASH";

my %cfg = %{$existing_cfg};

my @errors;

# FYTA-Token
my $token = trim($cgi->param("token") // "");

if ($token eq "") {
    push @errors, "Der FYTA-API-Token darf nicht leer sein.";
}
else {
    $cfg{FYTA_TOKEN} = $token;
}

# UDP aktiviert/deaktiviert
$cfg{UDP_ENABLED} =
    defined $cgi->param("udp_enabled")
    ? "true"
    : "false";

# UDP-Ziel
my $udp_host = trim($cgi->param("udp_host") // "");

if ($udp_host eq "") {
    push @errors, "Die UDP-Zieladresse darf nicht leer sein.";
}
else {
    $cfg{UDP_HOST} = $udp_host;
}

# UDP-Port
my $udp_port = trim($cgi->param("udp_port") // "");

if (
    $udp_port !~ /^\d+$/
    || $udp_port < 1
    || $udp_port > 65535
) {
    push @errors, "Der UDP-Port muss zwischen 1 und 65535 liegen.";
}
else {
    $cfg{UDP_PORT} = $udp_port;
}

# Abrufintervall in Minuten
my $interval = trim($cgi->param("interval") // "");

if (
    $interval !~ /^\d+$/
    || $interval < 1
    || $interval > 1440
) {
    push @errors, "Das Intervall muss zwischen 1 und 1440 Minuten liegen.";
}
else {
    $cfg{INTERVAL} = $interval;
}

my $saved = 0;
my $save_error = "";

if (!@errors) {
    eval {
        config::write_config(\%cfg);
        $saved = 1;
    };

    if ($@) {
        $save_error = $@;
        $save_error =~ s/\s+$//;
        push @errors, "Die Konfiguration konnte nicht gespeichert werden.";
    }
}

my $status_class = $saved ? "success" : "error";
my $status_title = $saved
    ? "Einstellungen gespeichert"
    : "Einstellungen nicht gespeichert";

my $status_text = $saved
    ? "Die Konfiguration wurde erfolgreich übernommen."
    : "Bitte korrigiere die folgenden Angaben.";

my $details_html = "";

if (@errors) {
    $details_html .= "<ul class=\"error-list\">\n";

    foreach my $error (@errors) {
        $details_html .=
            "    <li>" . html_escape($error) . "</li>\n";
    }

    $details_html .= "</ul>\n";
}

if ($save_error ne "") {
    $details_html .=
        "<details><summary>Technische Information</summary>"
        . "<pre>"
        . html_escape($save_error)
        . "</pre></details>";
}

require LoxBerry::Web;
use LoxBerry::System;

binmode STDOUT, ':encoding(UTF-8)';

LoxBerry::Web::lbheader("FYTA Connect – Speichern", "", "");
print <<'FYTA_STATIC';

<style>
.fyta-wrap{max-width:1000px;margin:0 auto;padding:8px 0 24px}.fyta-nav{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 18px}.fyta-nav a,.fyta-btn{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:10px 16px;border-radius:7px;background:#0b5cad!important;background-color:#0b5cad!important;color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:none!important;font-family:Arial,Helvetica,sans-serif!important;font-size:15px!important;line-height:1.25!important;font-weight:700!important;letter-spacing:0!important;text-decoration:none!important;border:1px solid #084a8a!important;box-shadow:0 1px 3px rgba(0,0,0,.18)!important;cursor:pointer;white-space:normal;text-align:center;box-sizing:border-box}.fyta-nav a:link,.fyta-nav a:visited,.fyta-nav a:hover,.fyta-nav a:active,.fyta-nav a:focus,.fyta-btn:link,.fyta-btn:visited,.fyta-btn:hover,.fyta-btn:active,.fyta-btn:focus{color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:none!important;text-decoration:none!important}.fyta-btn::-moz-focus-inner{border:0;padding:0}.fyta-nav a:hover,.fyta-btn:hover{background:#084a8a!important;background-color:#084a8a!important}.fyta-btn-green{background:#237a35!important;background-color:#237a35!important;border-color:#195d27!important}.fyta-btn-green:hover{background:#195d27!important;background-color:#195d27!important}.fyta-btn-grey{background:#455a64!important;background-color:#455a64!important;border-color:#34434a!important}.fyta-btn-grey:hover{background:#34434a!important;background-color:#34434a!important}.fyta-card{background:#fff;border:1px solid #dfe4e8;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:22px;margin-bottom:20px}.fyta-card h2{margin-top:0}.fyta-header-row{display:flex;justify-content:space-between;align-items:flex-start;gap:20px}.fyta-version{padding:6px 10px;background:#eceff1;border-radius:6px;color:#455a64;font-size:13px;font-weight:700;white-space:nowrap}.fyta-banner{padding:15px;margin-bottom:18px;border-radius:8px;font-weight:700}.fyta-ok{color:#1b5e20;background:#e8f5e9;border:1px solid #a5d6a7}.fyta-error{color:#b71c1c;background:#ffebee;border:1px solid #ef9a9a}.fyta-unknown{color:#5d4037;background:#fff8e1;border:1px solid #ffe082}.fyta-indicators{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:20px}.fyta-indicator,.fyta-stat{padding:15px;border-radius:8px;background:#f7f9fa;border:1px solid #e1e6e9}.fyta-small{color:#607d8b;font-size:13px;margin-bottom:6px}.fyta-good{color:#2e7d32;font-weight:700}.fyta-bad{color:#c62828;font-weight:700}.fyta-warn{color:#ef6c00;font-weight:700}.fyta-details,.fyta-form-grid,.fyta-result-grid{display:grid;grid-template-columns:220px 1fr;gap:12px 20px;align-items:center}.fyta-label{color:#607d8b;font-weight:700}.fyta-message{padding:14px;margin-top:20px;background:#f7f9fa;border-left:4px solid #1976d2;border-radius:4px;overflow-wrap:anywhere}.fyta-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.fyta-stat{text-align:center}.fyta-number{font-size:26px;font-weight:700;color:#1976d2;margin-bottom:5px}.fyta-actions{display:flex;flex-wrap:wrap;gap:12px}.fyta-form-grid input[type=text],.fyta-form-grid input[type=password],.fyta-form-grid input[type=number]{width:100%;padding:11px 12px;border:1px solid #b0bec5;border-radius:6px;box-sizing:border-box}.fyta-help{grid-column:2;color:#78909c;font-size:13px;margin-top:-8px}.fyta-token-row{display:flex;gap:8px}.fyta-token-row input{flex:1}.fyta-switch{display:flex;align-items:center;gap:10px}.fyta-switch input{width:20px;height:20px}.fyta-pre{overflow:auto;padding:16px;background:#17212b;color:#e5edf3;border-radius:7px;white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.45}.fyta-code{padding:3px 7px;background:#e8edf0;border-radius:4px}.fyta-error-list{margin:12px 0 0 20px}.fyta-footer{text-align:center;color:#78909c;font-size:13px;margin-top:20px}
@media(max-width:760px){.fyta-header-row{flex-direction:column}.fyta-indicators,.fyta-stats{grid-template-columns:1fr 1fr}.fyta-details,.fyta-form-grid,.fyta-result-grid{grid-template-columns:1fr;gap:6px}.fyta-help{grid-column:1;margin-top:0;margin-bottom:8px}.fyta-token-row{flex-direction:column}.fyta-btn,.fyta-nav a{width:100%;text-align:center;box-sizing:border-box}}
@media(max-width:480px){.fyta-indicators,.fyta-stats{grid-template-columns:1fr}}
</style>
<div class="fyta-wrap"><nav class="fyta-nav"><a href="index.cgi">Startseite</a><a href="settings.cgi">Einstellungen</a><a href="sync.cgi">Jetzt synchronisieren</a><a href="udp_test.cgi">UDP-Test</a></nav>
FYTA_STATIC
print <<"FYTA_HTML";
<section class="fyta-card"><h2>FYTA Connect</h2><div class="fyta-banner $status_class"><h3>$status_title</h3><p>$status_text</p>$details_html</div><div class="fyta-actions">
FYTA_HTML
if ($saved) { print <<'FYTA_STATIC';
<a class="fyta-btn fyta-btn-green" href="sync.cgi">Jetzt synchronisieren</a><a class="fyta-btn" href="udp_test.cgi">UDP testen</a>
FYTA_STATIC
}
print <<'FYTA_STATIC';
<a class="fyta-btn fyta-btn-grey" href="settings.cgi">Zurück zu den Einstellungen</a><a class="fyta-btn fyta-btn-grey" href="index.cgi">Zur Startseite</a></div></section>
FYTA_STATIC
print <<'FYTA_STATIC';
<div class="fyta-footer">FYTA Connect für LoxBerry</div></div>
FYTA_STATIC
LoxBerry::Web::lbfooter();
exit($saved ? 0 : 1);

sub trim
{
    my ($value) = @_;

    $value = "" unless defined $value;

    $value =~ s/^\s+//;
    $value =~ s/\s+$//;

    return $value;
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