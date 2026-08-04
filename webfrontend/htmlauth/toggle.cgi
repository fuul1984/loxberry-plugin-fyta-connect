#!/usr/bin/perl
use strict; use warnings; use utf8; use CGI;
use lib "/opt/loxberry/bin/plugins/fyta_connect"; use config;
my $cgi=CGI->new(); my $cfg=config::read_config(); $cfg={} unless $cfg && ref($cfg) eq 'HASH';
my $action=$cgi->param('action') // ''; $cfg->{PLUGIN_ENABLED}=$action eq 'enable' ? 'true' : 'false' if $action eq 'enable' || $action eq 'disable';
eval { config::write_config($cfg); };
print $cgi->redirect(-status=>303,-uri=>'index.cgi'); exit 0;
