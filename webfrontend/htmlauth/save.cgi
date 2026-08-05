#!/usr/bin/perl
use strict;use warnings;use utf8;use CGI;
use lib "/opt/loxberry/bin/plugins/fyta_connect";
use config;
require LoxBerry::Web;use LoxBerry::System;
binmode STDOUT, ':encoding(UTF-8)';
my $cgi=CGI->new;my $cfg=config::read_config();my @errors;
my $token=trim($cgi->param('token')//'');
$cfg->{FYTA_TOKEN}=$token;
push @errors,'Kein FYTA-Token gewählt.' if $token eq '';
$cfg->{UDP_ENABLED}=defined $cgi->param('udp_enabled')?'true':'false';
my $msno=trim($cgi->param('miniserver_no')//'');
my ($host,$name)=resolve_server($msno);
if(!$host){push @errors,'Bitte einen gültigen LoxBerry-Miniserver auswählen.';}else{$cfg->{MINISERVER_NO}=$msno;$cfg->{MINISERVER_NAME}=$name;$cfg->{UDP_HOST}=$host;$cfg->{LOXONE_HOST}=$host;}
my $port=trim($cgi->param('udp_port')//'');
if($port!~/^\d+$/||$port<1||$port>65535){push @errors,'Der UDP-Port muss zwischen 1 und 65535 liegen.'}else{$cfg->{UDP_PORT}=$port}
my $interval=trim($cgi->param('interval')//'');
if($interval!~/^\d+$/||$interval<1||$interval>1440){push @errors,'Das Intervall muss zwischen 1 und 1440 Minuten liegen.'}else{$cfg->{INTERVAL}=$interval}
my $saved=0;my $tech='';
if(!@errors){eval{config::write_config($cfg);$saved=1};if($@){$tech=$@;push @errors,'Die Konfiguration konnte nicht gespeichert werden.'}}
my $title=$saved?'Einstellungen gespeichert':'Einstellungen nicht gespeichert';my $class=$saved?'fyta-ok':'fyta-error';
my $details='';$details='<ul>'.join('',map{'<li>'.esc($_).'</li>'}@errors).'</ul>' if @errors;
LoxBerry::Web::lbheader('FYTA Connect – Speichern','','');
print <<'HTML';
<style>.fyta-wrap{max-width:900px;margin:auto}.fyta-card{background:#fff;border:1px solid #dfe4e8;border-radius:10px;padding:22px;margin-bottom:20px}.fyta-ok{background:#e8f5e9;border:1px solid #a5d6a7;color:#1b5e20;padding:16px;border-radius:8px}.fyta-error{background:#ffebee;border:1px solid #ef9a9a;color:#b71c1c;padding:16px;border-radius:8px}.fyta-actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:20px}.fyta-btn{display:inline-flex;padding:11px 17px;border-radius:7px;background:#0b5cad!important;color:#fff!important;text-decoration:none!important;font-weight:700!important}.fyta-grey{background:#455a64!important}</style><div class="fyta-wrap"><div class="fyta-card">
HTML
print qq{<div class="$class"><h2>$title</h2>$details</div><div class="fyta-actions">};
print '<a class="fyta-btn" href="sync.cgi">Jetzt synchronisieren</a>' if $saved;
print '<a class="fyta-btn fyta-grey" href="settings.cgi">Zurück zu den Einstellungen</a><a class="fyta-btn fyta-grey" href="index.cgi">Zur Startseite</a></div></div></div>';
LoxBerry::Web::lbfooter();exit($saved?0:1);
sub resolve_server {
    my ($wanted) = @_;
    my @servers = get_servers();

    for my $server (@servers) {
        next unless defined $wanted && length $wanted;
        return ($server->{host}, $server->{name})
            if "$server->{no}" eq "$wanted";
    }

    return;
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
        my $host = first(
            $entry,
            qw(IPAddress IPADDRESS Ipaddress ipaddress IP ip HOST Host host HOSTNAME Hostname hostname ADDRESS Address address)
        );
        next unless defined $host && length $host;
        next if $seen{lc($host)}++;

        $fallback_no++;
        my $no = first($entry, qw(MSNO msno NO no NUMBER number NR nr INDEX index));
        $no = $fallback_no unless defined $no && length $no;
        my $name = first(
            $entry,
            qw(NAME Name name MSNAME msname LOCATION Location location FRIENDLYNAME FriendlyName friendlyname)
        );
        $name = "Miniserver $no" unless defined $name && length $name;

        push @out, { no => "$no", name => "$name", host => "$host" };
    }

    return @out;
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

    my $host = first(
        $node,
        qw(IPAddress IPADDRESS Ipaddress ipaddress IP ip HOST Host host HOSTNAME Hostname hostname ADDRESS Address address)
    );
    push @{$out}, $node if defined $host && length $host;

    for my $value (values %{$node}) {
        collect_server_candidates($out, $value, $depth + 1)
            if ref($value) eq 'HASH' || ref($value) eq 'ARRAY';
    }
}

sub first {
    my ($h, @keys) = @_;
    for my $key (@keys) {
        return $h->{$key}
            if exists $h->{$key}
            && defined $h->{$key}
            && length $h->{$key};
    }
    return;
}

sub trim{my($v)=@_;$v='' unless defined$v;$v=~s/^\s+|\s+$//g;return$v}
sub esc{my($t)=@_;$t='' unless defined$t;$t=~s/&/&amp;/g;$t=~s/</&lt;/g;$t=~s/>/&gt;/g;$t=~s/"/&quot;/g;return$t}
