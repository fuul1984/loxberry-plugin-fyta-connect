#!/usr/bin/perl
use strict;
use warnings;
use utf8;

binmode STDOUT, ':encoding(UTF-8)';
use CGI;

my $cgi = CGI->new();
print $cgi->redirect('settings.cgi#udp-test');
exit 0;
