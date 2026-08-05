#!/usr/bin/perl
use strict;
use warnings;
use utf8;
use CGI;
use lib "/opt/loxberry/bin/plugins/fyta_connect";
use config;
require LoxBerry::Web;
use LoxBerry::System;

binmode STDOUT, ':encoding(UTF-8)';
my $cfg = config::read_config();
my $token = html_escape($cfg->{FYTA_TOKEN} // '');
my $port = html_escape($cfg->{UDP_PORT} // '5007');
my $interval = html_escape($cfg->{INTERVAL} // '15');
my $udp_enabled = ($cfg->{UDP_ENABLED} // 'true') eq 'true' ? 'checked' : '';
my $selected_no = $cfg->{MINISERVER_NO} // '';
my $current_host = $cfg->{UDP_HOST} // '';
my @servers = get_servers();
my $options = '';

if (@servers) {
    # Auswahlreihenfolge:
    # 1. gespeicherte Miniserver-Nummer
    # 2. gespeicherte IP/Hostname
    # 3. erster verfügbarer Miniserver
    my $selected_index = 0;
    my $found = 0;

    if (defined $selected_no && length $selected_no) {
        for my $i (0 .. $#servers) {
            if (defined $servers[$i]{no} && "$servers[$i]{no}" eq "$selected_no") {
                $selected_index = $i;
                $found = 1;
                last;
            }
        }
    }

    if (!$found && defined $current_host && length $current_host) {
        for my $i (0 .. $#servers) {
            if (lc($servers[$i]{host} // '') eq lc($current_host)) {
                $selected_index = $i;
                $found = 1;
                last;
            }
        }
    }

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


LoxBerry::Web::lbheader("FYTA Connect – Einstellungen", "", "");
print <<'HTML';
<style>
.fyta-wrap{max-width:1000px;margin:0 auto;padding:8px 0 24px}.fyta-nav,.fyta-actions{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 18px}.fyta-nav a,.fyta-btn{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:10px 16px;border-radius:7px;background:#0b5cad!important;color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:none!important;font-size:15px!important;font-weight:700!important;text-decoration:none!important;border:1px solid #084a8a!important;cursor:pointer}.fyta-btn:hover,.fyta-nav a:hover{background:#084a8a!important}.fyta-btn-green{background:#237a35!important;border-color:#195d27!important}.fyta-btn-green:hover{background:#195d27!important}.fyta-btn-grey{background:#455a64!important;border-color:#34434a!important}.fyta-card{background:#fff;border:1px solid #dfe4e8;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:22px;margin-bottom:20px}.fyta-form-grid{display:grid;grid-template-columns:220px 1fr;gap:12px 20px;align-items:center}.fyta-form-grid input,.fyta-form-grid select{width:100%;padding:11px 12px;border:1px solid #b0bec5;border-radius:6px;box-sizing:border-box;background:#fff}.fyta-help{grid-column:2;color:#78909c;font-size:13px;margin-top:-8px}.fyta-token-row{display:flex;gap:8px}.fyta-token-row input{flex:1}.fyta-switch{display:flex;align-items:center;gap:10px}.fyta-switch input{width:20px;height:20px}.fyta-footer{text-align:center;color:#78909c;font-size:13px;margin-top:20px}@media(max-width:760px){.fyta-form-grid{grid-template-columns:1fr;gap:6px}.fyta-help{grid-column:1;margin-top:0;margin-bottom:8px}.fyta-token-row{flex-direction:column}.fyta-btn,.fyta-nav a{width:100%;box-sizing:border-box}}
</style>
<div class="fyta-wrap"><nav class="fyta-nav"><a href="index.cgi">Startseite</a><a href="settings.cgi">Einstellungen</a><a href="sync.cgi">Jetzt synchronisieren</a><a href="udp_test.cgi">UDP-Test</a></nav>
HTML
print qq{
<section class="fyta-card"><h2>FYTA Connect – Einstellungen</h2><p>Token, LoxBerry-Miniserver, UDP-Port und Synchronisationsintervall konfigurieren.</p></section>
<form method="post" action="save.cgi">
<section class="fyta-card"><h2>FYTA API</h2><div class="fyta-form-grid">
<label for="token">API-Token</label><div class="fyta-token-row"><input id="token" type="password" name="token" value="$token" autocomplete="off"><button class="fyta-btn fyta-btn-grey" id="toggle-token" type="button" onclick="toggleToken()">Anzeigen</button></div><div class="fyta-help">Ohne Token ist das Plugin nicht betriebsbereit.</div>
</div></section>
<section class="fyta-card"><h2>UDP-Ausgabe</h2><div class="fyta-form-grid">
<label for="udp_enabled">UDP aktivieren</label><div class="fyta-switch"><input id="udp_enabled" type="checkbox" name="udp_enabled" $udp_enabled><span>Messwerte per UDP senden</span></div>
<label for="miniserver_no">Loxone Miniserver</label><select id="miniserver_no" name="miniserver_no" required>$options</select><div class="fyta-help">Die Liste wird direkt aus Einstellungen → Miniserver im LoxBerry gelesen.</div>
<label for="udp_port">UDP-Port</label><input id="udp_port" type="number" name="udp_port" value="$port" min="1" max="65535" required><div class="fyta-help">Port des virtuellen UDP-Eingangs in Loxone.</div>
</div></section>
<section class="fyta-card"><h2>Synchronisation</h2><div class="fyta-form-grid"><label for="interval">Abrufintervall</label><input id="interval" type="number" name="interval" value="$interval" min="1" max="1440" required><div class="fyta-help">Intervall in Minuten.</div></div></section>
<section class="fyta-card"><div class="fyta-actions"><button class="fyta-btn fyta-btn-green" type="submit">Einstellungen speichern</button><a class="fyta-btn" href="udp_test.cgi">UDP testen</a><a class="fyta-btn fyta-btn-grey" href="index.cgi">Abbrechen</a></div></section></form>
<script>function toggleToken(){const i=document.getElementById('token'),b=document.getElementById('toggle-token');if(i.type==='password'){i.type='text';b.textContent='Verbergen'}else{i.type='password';b.textContent='Anzeigen'}}</script>
};
print '<div class="fyta-footer">FYTA Connect für LoxBerry</div></div>';
LoxBerry::Web::lbfooter();
exit 0;

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
            qw(IPADDRESS Ipaddress ipaddress IP ip HOST Host host HOSTNAME hostname ADDRESS Address address)
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
        qw(IPADDRESS Ipaddress ipaddress IP ip HOST Host host HOSTNAME hostname ADDRESS Address address)
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
