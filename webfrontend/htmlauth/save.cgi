#!/usr/bin/perl
use strict;use warnings;use utf8;use CGI;use JSON qw(decode_json);
use lib "/opt/loxberry/bin/plugins/fyta_connect";
use config;
use auth_store;
use version;
use fyta_api;
require LoxBerry::Web;use LoxBerry::System;
binmode STDOUT, ':encoding(UTF-8)';
my $plugin_version = eval { LoxBerry::System::pluginversion('fyta_connect') };
$plugin_version = version::plugin_version() unless defined $plugin_version && length $plugin_version;
my $cgi=CGI->new;my $cfg=config::read_config();my @errors;
$cfg={} unless $cfg && ref($cfg) eq 'HASH';

my $old_email=trim($cfg->{FYTA_EMAIL}//'');
my $email=trim($cgi->param('email')//'');
my $password=$cgi->param('password')//'';
my $token=trim($cgi->param('token')//'');
$cfg->{FYTA_EMAIL}=$email;

my $auth=auth_store::load_auth();
my $auth_token_present=length($auth->{access_token}//'') || length($cfg->{FYTA_TOKEN}//'');
my $password_present=auth_store::has_password();

if(length($email) && $email !~ /^[^\s\@]+\@[^\s\@]+\.[^\s\@]+$/){
    push @errors,'Bitte eine gültige FYTA-E-Mail-Adresse eingeben.';
}
if(length($email) && $old_email ne '' && lc($email) ne lc($old_email) && $password eq ''){
    push @errors,'Bei einer geänderten FYTA-E-Mail muss das Passwort erneut eingegeben werden.';
}
if($password ne '' && $email eq ''){
    push @errors,'Für die automatische FYTA-Anmeldung wird die E-Mail-Adresse benötigt.';
}

$cfg->{UDP_ENABLED}=defined $cgi->param('udp_enabled')?'true':'false';
my $msno=trim($cgi->param('miniserver_no')//'');
my ($host,$name)=resolve_server($msno);
if(!$host){push @errors,'Bitte einen gültigen LoxBerry-Miniserver auswählen.';}else{$cfg->{MINISERVER_NO}=$msno;$cfg->{MINISERVER_NAME}=$name;$cfg->{UDP_HOST}=$host;$cfg->{LOXONE_HOST}=$host;}
my $port=trim($cgi->param('udp_port')//'');
if($port!~/^\d+$/||$port<1||$port>65535){push @errors,'Der UDP-Port muss zwischen 1 und 65535 liegen.'}else{$cfg->{UDP_PORT}=$port}
my $interval=trim($cgi->param('interval')//'');
if($interval!~/^\d+$/||$interval<1||$interval>1440){push @errors,'Das Intervall muss zwischen 1 und 1440 Minuten liegen.'}else{$cfg->{INTERVAL}=$interval}
my $sensor_meta=load_sensor_meta('/opt/loxberry/data/plugins/fyta_connect/sensor_meta.json');
$sensor_meta=merge_current_rows($sensor_meta,load_json_array('/opt/loxberry/data/plugins/fyta_connect/plants_cache.json'));
if(ref($sensor_meta) eq 'ARRAY'){
    for my $item (@{$sensor_meta}){
        next unless ref($item) eq 'HASH';
        my $id=$item->{config_id}//'';
        next unless $id =~ /^[A-Za-z0-9_]+$/;
        my $hours=trim($cgi->param("current_hours_$id")//'');
        if($hours eq ''){$hours=$item->{recommended_hours}//6;}
        if($hours!~/^\d+(?:\.\d+)?$/||$hours<1||$hours>168){
            push @errors,"Aktualitätsgrenze für ".($item->{plant_name}//$id)." muss zwischen 1 und 168 Stunden liegen.";
        }else{
            $cfg->{"CURRENT_MAX_AGE_HOURS_$id"}=$hours;
            my $plant_cfg_id=$item->{plant_config_id}//stable_plant_config_id($item->{plant_id});
            $cfg->{"SEND_CURRENT_$plant_cfg_id"}=defined $cgi->param("send_current_$id")?'true':'false';
        }
    }
}

my $login;
if(!@errors && $password ne ''){
    $login=fyta_api::login($email,$password);
    push @errors,(fyta_api::last_error() || 'FYTA-Anmeldung fehlgeschlagen. Zugangsdaten prüfen.') unless $login && ref($login) eq 'HASH';
}

my $saved=0;my $tech='';
if(!@errors){
    eval{
        if($login && ref($login) eq 'HASH'){
            auth_store::store_password($password);
            my $expires_in=$login->{expires_in};
            $expires_in=0 unless defined $expires_in && $expires_in =~ /^\d+$/;
            auth_store::store_session(
                email=>$email,
                access_token=>$login->{access_token},
                refresh_token=>($login->{refresh_token}//''),
                expires_at=>($expires_in>0?time()+$expires_in:0),
            );
            $cfg->{FYTA_TOKEN}='';
            $auth_token_present=1;
            $password_present=1;
        } elsif(length($token)) {
            auth_store::store_session(email=>$email,access_token=>$token,refresh_token=>'',expires_at=>0);
            $cfg->{FYTA_TOKEN}='';
            $auth_token_present=1;
        } elsif(length($cfg->{FYTA_TOKEN}//'')) {
            auth_store::import_legacy_token($cfg->{FYTA_TOKEN});
            $cfg->{FYTA_TOKEN}='';
            $auth_token_present=1;
        }
        die "Keine FYTA-Anmeldung vorhanden.\n" unless $auth_token_present || ($email ne '' && $password_present);
        config::write_config($cfg);
        $saved=1;
    };
    if($@){$tech=$@;push @errors,'Die Konfiguration bzw. FYTA-Anmeldung konnte nicht sicher gespeichert werden.'}
}
my $title=$saved?'Einstellungen gespeichert':'Einstellungen nicht gespeichert';my $class=$saved?'fyta-ok':'fyta-error';
my $details='';$details='<ul>'.join('',map{'<li>'.esc($_).'</li>'}@errors).'</ul>' if @errors;
LoxBerry::Web::lbheader('FYTA Connect – Speichern','','');
print <<'HTML';
<style>.fyta-wrap{max-width:900px;margin:auto}.fyta-card{background:#fff;border:1px solid #dfe4e8;border-radius:10px;padding:22px;margin-bottom:20px}.fyta-ok{background:#e8f5e9;border:1px solid #a5d6a7;color:#1b5e20;padding:16px;border-radius:8px}.fyta-error{background:#ffebee;border:1px solid #ef9a9a;color:#b71c1c;padding:16px;border-radius:8px}.fyta-actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:20px}.fyta-btn{display:inline-flex;padding:11px 17px;border-radius:7px;background:#0b5cad!important;color:#fff!important;text-decoration:none!important;font-weight:700!important}.fyta-grey{background:#455a64!important}@media(max-width:760px){.fyta-wrap{width:100%;max-width:100%;padding:4px 8px 20px;box-sizing:border-box}.fyta-card{padding:15px 12px;box-sizing:border-box;overflow:hidden}.fyta-actions{display:grid;grid-template-columns:1fr;gap:8px}.fyta-btn{width:100%;max-width:100%;min-height:44px;align-items:center;justify-content:center;text-align:center;box-sizing:border-box;white-space:normal;overflow-wrap:anywhere}.fyta-ok,.fyta-error{padding:13px;overflow-wrap:anywhere;word-break:break-word}}.fyta-btn,.fyta-btn:link,.fyta-btn:visited,.fyta-btn:hover,.fyta-btn:focus,.fyta-btn:active{color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:none!important;text-decoration:none!important;opacity:1!important}.fyta-btn:hover,.fyta-btn:focus,.fyta-btn:active{background:#084a8a!important}.fyta-grey:hover,.fyta-grey:focus,.fyta-grey:active{background:#34434a!important}.fyta-btn:focus{outline:3px solid rgba(11,92,173,.30)!important;outline-offset:2px!important}</style><div class="fyta-wrap"><div class="fyta-card">
HTML
print qq{<div class="$class"><h2>$title</h2>$details</div><div class="fyta-actions">};
print '<a class="fyta-btn" href="sync.cgi">Jetzt synchronisieren</a>' if $saved;
print '<a class="fyta-btn fyta-grey" href="settings.cgi">Zurück zu den Einstellungen</a><a class="fyta-btn fyta-grey" href="index.cgi">Zur Startseite</a></div><p style="color:#78909c;font-size:13px">FYTA Connect · Version '.esc($plugin_version).'</p></div></div>';
LoxBerry::Web::lbfooter();exit($saved?0:1);
sub load_sensor_meta{
    my($file)=@_;return [] unless -f $file;
    open(my $fh,'<',$file) or return [];local $/;my $content=<$fh>;close $fh;
    my $data;eval{$data=decode_json($content)};return [] if $@||ref($data) ne 'ARRAY';return $data;
}

sub load_json_array {
    my($file)=@_;return [] unless defined $file && -f $file;
    open(my $fh,'<',$file) or return [];local $/;my $content=<$fh>;close $fh;
    my $data;eval{$data=decode_json($content)};return [] if $@||ref($data) ne 'ARRAY';return $data;
}

sub merge_current_rows {
    my($meta,$plants)=@_;$meta=[] unless ref($meta) eq 'ARRAY';$plants=[] unless ref($plants) eq 'ARRAY';
    my @rows=@{$meta};my %known=map {defined($_->{plant_id})?("$_->{plant_id}"=>1):()} grep {ref($_) eq 'HASH'} @rows;
    for my $plant (@{$plants}){
        next unless ref($plant) eq 'HASH' && defined $plant->{id};next if $known{"$plant->{id}"};
        my $pid=$plant->{id};my $pcid=stable_plant_config_id($pid);
        push @rows,{plant_id=>$pid,plant_name=>($plant->{nickname}//$plant->{name}//'Unbekannt'),config_id=>$pcid,plant_config_id=>$pcid,recommended_hours=>6};
    }
    return \@rows;
}

sub stable_plant_config_id {
    my ($plant_id)=@_;
    my $id='PLANT_'.(defined $plant_id ? $plant_id : 'UNKNOWN');
    $id =~ s/[^A-Za-z0-9_]/_/g;
    return uc($id);
}

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
