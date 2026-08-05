package config;

use strict;
use warnings;
use File::Basename qw(dirname);
use File::Path qw(make_path);

our $CONFIG_FILE = "/opt/loxberry/config/plugins/fyta_connect/fyta.cfg";

our %DEFAULTS = (
    PLUGIN_ENABLED => 'true',
    FYTA_TOKEN      => '',
    MINISERVER_NO   => '1',
    UDP_ENABLED     => 'true',
    UDP_HOST        => '',
    UDP_PORT        => '5007',
    INTERVAL        => '15',
    LOXONE_SSL      => 'false',
    LOXONE_HOST     => '',
    LOXONE_PORT     => '443',
    LOXONE_USER     => '',
    LOXONE_PASSWORD => '',
);

sub read_config
{
    my %cfg = %DEFAULTS;

    return \%cfg unless -f $CONFIG_FILE;

    open(my $fh, '<', $CONFIG_FILE)
        or return \%cfg;

    while (my $line = <$fh>) {
        chomp $line;
        $line =~ s/\r//g;

        next if $line =~ /^\s*$/;
        next if $line =~ /^\s*[#;]/;

        if ($line =~ /^\s*([^=]+?)\s*=\s*(.*?)\s*$/) {
            $cfg{$1} = $2;
        }
    }

    close $fh;
    return \%cfg;
}

sub write_config
{
    my ($cfg) = @_;
    die "Ungültige Konfiguration.\n"
        unless $cfg && ref($cfg) eq 'HASH';

    my %merged = (%DEFAULTS, %{$cfg});
    my $dir = dirname($CONFIG_FILE);
    make_path($dir, { mode => 0750 }) unless -d $dir;

    my $temp = "$CONFIG_FILE.tmp.$$";
    open(my $fh, '>', $temp)
        or die "Kann Konfigurationsdatei nicht schreiben: $!\n";

    # Bewusst feste Reihenfolge für bessere Lesbarkeit und Upgrade-Stabilität.
    my @ordered = qw(
        PLUGIN_ENABLED FYTA_TOKEN MINISERVER_NO UDP_ENABLED UDP_HOST UDP_PORT
        INTERVAL LOXONE_SSL LOXONE_HOST LOXONE_PORT LOXONE_USER LOXONE_PASSWORD
    );
    my %written;

    for my $key (@ordered, sort keys %merged) {
        next if $written{$key}++;
        my $value = defined $merged{$key} ? $merged{$key} : '';
        $value =~ s/[\r\n]//g;
        print {$fh} "$key=$value\n";
    }

    close $fh or die "Kann Konfigurationsdatei nicht schließen: $!\n";
    chmod 0600, $temp;
    rename($temp, $CONFIG_FILE)
        or die "Kann Konfigurationsdatei nicht ersetzen: $!\n";

    return 1;
}

sub ensure_defaults
{
    my $cfg = read_config();
    return write_config($cfg);
}

1;
