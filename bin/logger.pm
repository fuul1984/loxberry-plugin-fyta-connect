package logger;

use strict;
use warnings;

use POSIX qw(strftime);
use File::Path qw(make_path);

our $LOG_DIR       = "/opt/loxberry/log/plugins/fyta_connect";
our $LOG_FILE      = "$LOG_DIR/fyta_connect.log";

# Maximale Loggröße (1 MB)
our $MAX_LOG_SIZE  = 1024 * 1024;

# Einstellungen
our $CONSOLE       = 1;    # Ausgabe auf STDOUT
our $DEBUG         = 0;    # Debugmeldungen schreiben

#########################################################
# öffentliche Funktionen
#########################################################

sub set_debug
{
    my ($enabled) = @_;
    $DEBUG = $enabled ? 1 : 0;
}

sub info
{
    _write("INFO", shift);
}

sub warning
{
    _write("WARNING", shift);
}

sub error
{
    _write("ERROR", shift);
}

sub debug
{
    return unless $DEBUG;
    _write("DEBUG", shift);
}

#########################################################
# interne Funktionen
#########################################################

sub _write
{
    my ($level, $text) = @_;

    $text //= "";

    # Mehrzeilige Texte vermeiden
    $text =~ s/\r//g;
    $text =~ s/\n/ /g;

    _prepare_log_directory();
    _rotate_log_if_needed();

    my $timestamp = strftime(
        "%Y-%m-%d %H:%M:%S",
        localtime()
    );

    my $line = sprintf(
        "%s %-7s %s\n",
        $timestamp,
        $level,
        $text
    );

    #
    # Ausgabe auf Konsole
    #
    print $line if $CONSOLE;

    #
    # Ausgabe in Datei
    #
    if (open(my $fh, ">>", $LOG_FILE)) {
        print $fh $line;
        close($fh);
    }
}

#########################################################

sub _prepare_log_directory
{
    return if -d $LOG_DIR;

    eval {
        make_path(
            $LOG_DIR,
            {
                mode => 0750
            }
        );
    };
}

#########################################################

sub _rotate_log_if_needed
{
    return unless -f $LOG_FILE;

    return unless -s $LOG_FILE > $MAX_LOG_SIZE;

    unlink($LOG_FILE);

    if (open(my $fh, ">", $LOG_FILE)) {

        my $timestamp = strftime(
            "%Y-%m-%d %H:%M:%S",
            localtime()
        );

        print $fh
"$timestamp INFO    Logdatei automatisch zurückgesetzt (Größe > 1 MB)\n";

        close($fh);
    }
}

1;