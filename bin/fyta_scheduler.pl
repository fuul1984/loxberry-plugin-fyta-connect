#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDOUT, ":encoding(UTF-8)";
binmode STDERR, ":encoding(UTF-8)";

use Fcntl qw(:flock);
use File::Path qw(make_path);

use lib "/opt/loxberry/bin/plugins/fyta_connect";

use config;

my $plugin_dir = "/opt/loxberry/bin/plugins/fyta_connect";
my $data_dir   = "/opt/loxberry/data/plugins/fyta_connect";

my $main_script = "$plugin_dir/fyta_connect.pl";
my $state_file  = "$data_dir/last_run.timestamp";
my $lock_file   = "$data_dir/scheduler.lock";

make_path($data_dir, { mode => 0750 }) unless -d $data_dir;

open(my $lock_fh, ">>", $lock_file)
    or die "Kann Sperrdatei nicht öffnen: $!\n";

exit 0 unless flock($lock_fh, LOCK_EX | LOCK_NB);

my $cfg = config::read_config();

die "Konfiguration konnte nicht gelesen werden\n"
    unless $cfg && ref($cfg) eq "HASH";

# Bei deaktiviertem Plugin keine API-Abfrage und keinen UDP-Versand ausführen.
exit 0 unless ($cfg->{PLUGIN_ENABLED} // "true") eq "true";

my $interval = $cfg->{INTERVAL};
$interval = 15 unless defined $interval && $interval =~ /^\d+$/;

die "INTERVAL muss zwischen 1 und 1440 Minuten liegen\n"
    if $interval < 1 || $interval > 1440;

die "Hauptprogramm nicht gefunden: $main_script\n"
    unless -f $main_script;

my $last_run = 0;

if (-f $state_file && open(my $state_fh, "<", $state_file)) {
    my $value = <$state_fh>;
    close $state_fh;
    chomp $value if defined $value;
    $last_run = $value if defined $value && $value =~ /^\d+$/;
}

my $now = time();
my $interval_seconds = $interval * 60;

exit 0 if $last_run > 0 && ($now - $last_run) < $interval_seconds;

my $result = system("/usr/bin/perl", $main_script);

if ($result == -1) {
    die "fyta_connect.pl konnte nicht gestartet werden: $!\n";
}

my $exit_code = $result >> 8;

# Nur erfolgreiche Worker-Läufe verschieben den regulären Intervallzeitpunkt.
# Nach Reboot-, Netzwerk- oder temporären API-Fehlern versucht der minütliche
# LoxBerry-Cron dadurch beim nächsten Lauf automatisch erneut.
if ($exit_code == 0) {
    if (open(my $state_fh, ">", $state_file)) {
        print $state_fh time();
        close $state_fh;
    }
    else {
        die "Kann Zeitstempel nicht speichern: $!\n";
    }
}
else {
    die "fyta_connect.pl endete mit Fehlercode $exit_code\n";
}

exit 0;
