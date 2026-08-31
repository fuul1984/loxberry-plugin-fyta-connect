#!/usr/bin/perl

use strict;
use warnings;
use utf8;
use Encode qw(decode FB_CROAK);

binmode STDOUT, ':encoding(UTF-8)';

my $script =
    '/opt/loxberry/bin/plugins/fyta_connect/fyta_connect.pl';

my $output = '';
my $exit_code;
my $timed_out = 0;

if (!-f $script) {
    $output = "Hauptprogramm nicht gefunden:\n$script";
    $exit_code = 1;
}
elsif (!-r $script) {
    $output = "Hauptprogramm kann nicht gelesen werden:\n$script";
    $exit_code = 1;
}
else {
    eval {
        local $SIG{ALRM} = sub {
            die "TIMEOUT\n";
        };

        alarm 90;

        $output = qx{/usr/bin/perl "$script" 2>&1};
        # qx{} liefert rohe UTF-8-Bytes des Workers. Vor der HTML-Ausgabe
        # einmal dekodieren, damit STDOUT sie nicht ein zweites Mal kodiert.
        if (defined $output && length $output && !utf8::is_utf8($output)) {
            my $decoded = eval { decode("UTF-8", $output, FB_CROAK) };
            $output = $decoded if defined $decoded && !$@;
        }
        $exit_code = $? >> 8;

        alarm 0;
    };

    if ($@) {
        alarm 0;

        if ($@ eq "TIMEOUT\n") {
            $timed_out = 1;
            $output .= "\nSynchronisation nach 90 Sekunden abgebrochen.";
            $exit_code = 1;
        }
        else {
            $output .= "\nInterner Fehler: $@";
            $exit_code = 1;
        }
    }
}

$output = 'Das Hauptprogramm hat keine Ausgabe erzeugt.'
    unless defined $output && length $output;

my $safe_output = html_escape($output);

my $status_class =
    defined $exit_code && $exit_code == 0
    ? 'success'
    : 'error';

my $status_text =
    defined $exit_code && $exit_code == 0
    ? 'Synchronisation erfolgreich abgeschlossen'
    : 'Synchronisation mit Fehler beendet';

$status_text =
    'Synchronisation wegen Zeitüberschreitung abgebrochen'
    if $timed_out;

use lib "/opt/loxberry/bin/plugins/fyta_connect";
use version;
require LoxBerry::Web;
use LoxBerry::System;

binmode STDOUT, ':encoding(UTF-8)';
my $plugin_version = eval { LoxBerry::System::pluginversion('fyta_connect') };
$plugin_version = version::plugin_version() unless defined $plugin_version && length $plugin_version;
my $safe_plugin_version = html_escape($plugin_version);

LoxBerry::Web::lbheader("FYTA Connect – Synchronisation", "", "");
print <<'FYTA_STATIC';

<style>
.fyta-wrap{max-width:1000px;margin:0 auto;padding:8px 0 24px}.fyta-nav{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 18px}.fyta-nav a,.fyta-btn{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:10px 16px;border-radius:7px;background:#1976d2;color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:none!important;font-family:Arial,Helvetica,sans-serif!important;font-size:15px!important;line-height:1.25!important;font-weight:700!important;letter-spacing:0!important;text-decoration:none!important;border:0!important;box-shadow:none!important;cursor:pointer;white-space:normal;text-align:center;box-sizing:border-box}.fyta-nav a:link,.fyta-nav a:visited,.fyta-nav a:hover,.fyta-nav a:active,.fyta-nav a:focus,.fyta-btn:link,.fyta-btn:visited,.fyta-btn:hover,.fyta-btn:active,.fyta-btn:focus{color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:none!important;text-decoration:none!important}.fyta-btn::-moz-focus-inner{border:0;padding:0}.fyta-nav a:hover,.fyta-btn:hover{background:#125ea8}.fyta-btn-green{background:#2e7d32}.fyta-btn-green:hover{background:#216425}.fyta-btn-grey{background:#546e7a}.fyta-btn-grey:hover{background:#40545d}.fyta-card{background:#fff;border:1px solid #dfe4e8;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:22px;margin-bottom:20px}.fyta-card h2{margin-top:0}.fyta-header-row{display:flex;justify-content:space-between;align-items:flex-start;gap:20px}.fyta-version{padding:6px 10px;background:#eceff1;border-radius:6px;color:#455a64;font-size:13px;font-weight:700;white-space:nowrap}.fyta-banner{padding:15px;margin-bottom:18px;border-radius:8px;font-weight:700}.fyta-ok{color:#1b5e20;background:#e8f5e9;border:1px solid #a5d6a7}.fyta-error{color:#b71c1c;background:#ffebee;border:1px solid #ef9a9a}.fyta-unknown{color:#5d4037;background:#fff8e1;border:1px solid #ffe082}.fyta-indicators{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:20px}.fyta-indicator,.fyta-stat{padding:15px;border-radius:8px;background:#f7f9fa;border:1px solid #e1e6e9}.fyta-small{color:#607d8b;font-size:13px;margin-bottom:6px}.fyta-good{color:#2e7d32;font-weight:700}.fyta-bad{color:#c62828;font-weight:700}.fyta-warn{color:#ef6c00;font-weight:700}.fyta-details,.fyta-form-grid,.fyta-result-grid{display:grid;grid-template-columns:220px 1fr;gap:12px 20px;align-items:center}.fyta-label{color:#607d8b;font-weight:700}.fyta-message{padding:14px;margin-top:20px;background:#f7f9fa;border-left:4px solid #1976d2;border-radius:4px;overflow-wrap:anywhere}.fyta-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.fyta-stat{text-align:center}.fyta-number{font-size:26px;font-weight:700;color:#1976d2;margin-bottom:5px}.fyta-actions{display:flex;flex-wrap:wrap;gap:12px}.fyta-form-grid input[type=text],.fyta-form-grid input[type=password],.fyta-form-grid input[type=number]{width:100%;padding:11px 12px;border:1px solid #b0bec5;border-radius:6px;box-sizing:border-box}.fyta-help{grid-column:2;color:#78909c;font-size:13px;margin-top:-8px}.fyta-token-row{display:flex;gap:8px}.fyta-token-row input{flex:1}.fyta-switch{display:flex;align-items:center;gap:10px}.fyta-switch input{width:20px;height:20px}.fyta-pre{overflow:auto;padding:16px;background:#17212b;color:#e5edf3;border-radius:7px;white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.45}.fyta-code{padding:3px 7px;background:#e8edf0;border-radius:4px}.fyta-error-list{margin:12px 0 0 20px}.fyta-footer{text-align:center;color:#78909c;font-size:13px;margin-top:20px}
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
<section class="fyta-card"><h2>Synchronisation</h2><div class="fyta-banner $status_class">$status_text</div><h3>Programmausgabe</h3><pre class="fyta-pre">$safe_output</pre><div class="fyta-actions"><a class="fyta-btn" href="sync.cgi">Erneut synchronisieren</a><a class="fyta-btn fyta-btn-grey" href="index.cgi">Zurück zur Startseite</a></div></section>
FYTA_HTML
print <<"FYTA_FOOTER";
<div class="fyta-footer">FYTA Connect für LoxBerry · Version $safe_plugin_version</div></div>
FYTA_FOOTER
LoxBerry::Web::lbfooter();
exit 0;

sub html_escape
{
    my ($text) = @_;

    $text = '' unless defined $text;

    $text =~ s/&/&amp;/g;
    $text =~ s/</&lt;/g;
    $text =~ s/>/&gt;/g;
    $text =~ s/"/&quot;/g;
    $text =~ s/'/&#39;/g;

    return $text;
}