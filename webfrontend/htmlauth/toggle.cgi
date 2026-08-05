#!/usr/bin/perl
use strict;use warnings;use utf8;use CGI;
use lib "/opt/loxberry/bin/plugins/fyta_connect";
use config;
my $q=CGI->new;my $action=$q->param('action')//'';my $cfg=config::read_config();
$cfg->{PLUGIN_ENABLED}=($action eq 'enable')?'true':'false';
config::write_config($cfg);
print $q->redirect('index.cgi');
exit 0;
