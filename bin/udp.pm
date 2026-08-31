package udp;

use strict;
use warnings;
use utf8;

use IO::Socket::INET;

sub send_udp
{
    my ($host, $port, $message) = @_;

    return 'ERROR: Host fehlt'
        unless defined $host && length $host;

    return 'ERROR: Port fehlt'
        unless defined $port && $port =~ /^\d+$/;

    return 'ERROR: Ungültiger Port'
        if $port < 1 || $port > 65535;

    return 'ERROR: Nachricht fehlt'
        unless defined $message && length $message;

    my $socket = IO::Socket::INET->new(
        PeerAddr => $host,
        PeerPort => $port,
        Proto    => 'udp'
    );

    unless ($socket) {
        return "ERROR: UDP Socket konnte nicht erstellt werden: $!";
    }

    my $bytes_sent = $socket->send($message);

    unless (defined $bytes_sent) {
        $socket->close();
        return "ERROR: UDP Versand fehlgeschlagen: $!";
    }

    $socket->close();

    return "OK: $bytes_sent Bytes gesendet";
}

1;