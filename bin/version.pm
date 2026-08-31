package version;

use strict;
use warnings;

our @PLUGIN_CFG_CANDIDATES = (
    "/opt/loxberry/bin/plugins/fyta_connect/plugin.cfg",
    "/opt/loxberry/config/plugins/fyta_connect/plugin.cfg",
);

sub plugin_version
{
    my ($file) = @_;
    if (!defined $file || !length $file) {
        ($file) = grep { -f $_ } @PLUGIN_CFG_CANDIDATES;
    }

    return 'unknown' unless defined $file && -f $file;
    open(my $fh, '<', $file) or return 'unknown';

    while (my $line = <$fh>) {
        $line =~ s/\r//g;
        if ($line =~ /^\s*VERSION\s*=\s*(.*?)\s*$/) {
            close $fh;
            return length($1) ? $1 : 'unknown';
        }
    }

    close $fh;
    return 'unknown';
}

1;
