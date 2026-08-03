package config;

use strict;
use warnings;

our $CONFIG_FILE =
    "/opt/loxberry/config/plugins/fyta_connect/fyta.cfg";

sub read_config
{
    my %cfg;

    open(my $fh, "<", $CONFIG_FILE)
        or die "Kann Konfigurationsdatei nicht öffnen: $CONFIG_FILE\n";

    while (my $line = <$fh>)
    {
        chomp($line);

        $line =~ s/\r//g;

        next if $line =~ /^\s*$/;
        next if $line =~ /^\s*#/;
        next if $line =~ /^\s*;/;

        if ($line =~ /^\s*([^=]+?)\s*=\s*(.*?)\s*$/)
        {
            $cfg{$1} = $2;
        }
    }

    close($fh);

    return \%cfg;
}

sub write_config
{
    my ($cfg) = @_;

    open(my $fh, ">", $CONFIG_FILE)
        or die "Kann Konfigurationsdatei nicht schreiben.\n";

    foreach my $key (sort keys %{$cfg})
    {
        my $value = defined $cfg->{$key}
            ? $cfg->{$key}
            : "";

        print $fh "$key=$value\n";
    }

    close($fh);

    return 1;
}

1;