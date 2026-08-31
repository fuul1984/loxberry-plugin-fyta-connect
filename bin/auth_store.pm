package auth_store;

use strict;
use warnings;
use utf8;
use File::Path qw(make_path);
use JSON qw(encode_json decode_json);
use IPC::Open3;
use Symbol qw(gensym);

our $DATA_DIR  = '/opt/loxberry/data/plugins/fyta_connect';
our $AUTH_FILE = "$DATA_DIR/auth.json";
our $KEY_FILE  = "$DATA_DIR/.auth.key";

sub load_auth
{
    return {} unless -f $AUTH_FILE;
    open(my $fh, '<', $AUTH_FILE) or return {};
    local $/;
    my $raw = <$fh>;
    close $fh;
    my $data;
    eval { $data = decode_json($raw // ''); };
    return {} if $@ || ref($data) ne 'HASH';
    return $data;
}

sub save_auth
{
    my ($auth) = @_;
    die "Ungültige Authentifizierungsdaten.\n" unless ref($auth) eq 'HASH';
    _ensure_dir();
    my $tmp = "$AUTH_FILE.tmp.$$";
    open(my $fh, '>', $tmp) or die "Kann Authentifizierungsdaten nicht schreiben: $!\n";
    print {$fh} encode_json($auth);
    close $fh or die "Kann Authentifizierungsdaten nicht schließen: $!\n";
    chmod 0600, $tmp;
    rename($tmp, $AUTH_FILE) or die "Kann Authentifizierungsdaten nicht ersetzen: $!\n";
    chmod 0600, $AUTH_FILE;
    return 1;
}

sub store_password
{
    my ($password) = @_;
    die "Leeres Passwort kann nicht gespeichert werden.\n" unless defined $password && length $password;
    my $cipher = _openssl_crypt(1, $password);
    my $auth = load_auth();
    $auth->{password_enc} = $cipher;
    $auth->{password_format} = 'openssl-aes-256-cbc-pbkdf2-v1';
    save_auth($auth);
    return 1;
}

sub load_password
{
    my $auth = load_auth();
    return '' unless defined $auth->{password_enc} && length $auth->{password_enc};
    return _openssl_crypt(0, $auth->{password_enc});
}

sub store_session
{
    my (%args) = @_;
    my $auth = load_auth();
    $auth->{email} = $args{email} if defined $args{email};
    $auth->{access_token} = $args{access_token} if defined $args{access_token};
    $auth->{refresh_token} = $args{refresh_token} if defined $args{refresh_token};
    $auth->{expires_at} = $args{expires_at} if defined $args{expires_at};
    $auth->{updated_at} = time();
    save_auth($auth);
    return 1;
}

sub import_legacy_token
{
    my ($token) = @_;
    return 0 unless defined $token && length $token;
    my $auth = load_auth();
    return 0 if defined $auth->{access_token} && length($auth->{access_token} // '');
    $auth->{access_token} = $token;
    $auth->{legacy_token} = 1;
    $auth->{updated_at} = time();
    save_auth($auth);
    return 1;
}

sub clear_session
{
    my $auth = load_auth();
    delete @{$auth}{qw(access_token refresh_token expires_at legacy_token)};
    save_auth($auth);
    return 1;
}

sub has_password
{
    my $auth = load_auth();
    return defined $auth->{password_enc} && length($auth->{password_enc} // '') ? 1 : 0;
}

sub _ensure_dir
{
    make_path($DATA_DIR, { mode => 0750 }) unless -d $DATA_DIR;
    chmod 0750, $DATA_DIR;
}

sub _ensure_key
{
    _ensure_dir();
    if (!-f $KEY_FILE) {
        open(my $ur, '<:raw', '/dev/urandom') or die "Kann Zufallsquelle nicht lesen: $!\n";
        my $bytes = '';
        my $got = read($ur, $bytes, 32);
        close $ur;
        die "Konnte keinen sicheren Schlüssel erzeugen.\n" unless defined $got && $got == 32;
        my $hex = unpack('H*', $bytes);
        my $tmp = "$KEY_FILE.tmp.$$";
        open(my $fh, '>', $tmp) or die "Kann Schlüsseldatei nicht schreiben: $!\n";
        print {$fh} $hex;
        close $fh;
        chmod 0600, $tmp;
        rename($tmp, $KEY_FILE) or die "Kann Schlüsseldatei nicht ersetzen: $!\n";
    }
    chmod 0600, $KEY_FILE;
    return $KEY_FILE;
}

sub _openssl_crypt
{
    my ($encrypt, $input) = @_;
    my $openssl = -x '/usr/bin/openssl' ? '/usr/bin/openssl' : (-x '/bin/openssl' ? '/bin/openssl' : '');
    die "OpenSSL ist nicht verfügbar; Passwort kann nicht sicher gespeichert werden.\n" unless length $openssl;
    my $keyfile = _ensure_key();
    my @cmd = ($openssl, 'enc', '-aes-256-cbc', '-pbkdf2', '-salt', '-a', '-A', '-pass', "file:$keyfile");
    push @cmd, '-d' unless $encrypt;

    my $err = gensym;
    my ($in, $out);
    my $pid = open3($in, $out, $err, @cmd);
    binmode $in;
    binmode $out;
    print {$in} $input;
    close $in;
    local $/;
    my $result = <$out> // '';
    my $error = <$err> // '';
    close $out;
    close $err;
    waitpid($pid, 0);
    my $rc = $? >> 8;
    die "Passwortverschlüsselung fehlgeschlagen.\n" if $rc != 0;
    $result =~ s/[\r\n]+$//;
    return $result;
}

1;
