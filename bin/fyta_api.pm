package fyta_api;

use strict;
use warnings;
use utf8;

use LWP::UserAgent;
use HTTP::Request;
use JSON qw(encode_json decode_json);
use MIME::Base64 qw(encode_base64);

my $BASE_URL = 'https://web.fyta.de';
our $LAST_HTTP_STATUS = 0;
our $LAST_ERROR = '';

sub _ua
{
    my $ua = LWP::UserAgent->new;
    $ua->timeout(20);
    $ua->agent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/150.0');
    $ua->default_header(
        'Accept'          => 'application/json, text/plain, */*',
        'Referer'         => 'https://web.fyta.de/',
        'Accept-Language' => 'de-CH,de;q=0.9,en-US;q=0.8,en;q=0.7'
    );
    return $ua;
}

sub last_http_status { return $LAST_HTTP_STATUS; }
sub last_error       { return $LAST_ERROR; }

sub login
{
    my ($email, $password) = @_;
    $LAST_HTTP_STATUS = 0;
    $LAST_ERROR = '';
    return undef unless defined $email && length $email;
    return undef unless defined $password && length $password;

    my $ua = _ua();
    my $request = HTTP::Request->new('POST', "$BASE_URL/api/auth/login");
    $request->header('Content-Type' => 'application/json');
    $request->header('Authorization' => 'Basic ' . encode_base64("$email:$password", ''));
    $request->content(encode_json({ email => $email, password => $password }));

    my $response = $ua->request($request);
    $LAST_HTTP_STATUS = $response->code || 0;
    unless ($response->is_success) {
        $LAST_ERROR = 'FYTA-Anmeldung fehlgeschlagen (HTTP ' . ($response->code || '?') . ')';
        return undef;
    }

    my $json;
    eval { $json = decode_json($response->decoded_content); };
    if ($@ || ref($json) ne 'HASH' || !defined($json->{access_token}) || !length($json->{access_token})) {
        $LAST_ERROR = 'FYTA-Anmeldung lieferte keine gültigen Token-Daten';
        return undef;
    }
    return $json;
}

sub api_get
{
    my ($token, $url) = @_;
    $LAST_HTTP_STATUS = 0;
    $LAST_ERROR = '';
    return undef unless defined $token && length $token;
    return undef unless defined $url && length $url;

    my $ua = _ua();
    my $response = $ua->get($url, 'Authorization' => "Bearer $token");
    $LAST_HTTP_STATUS = $response->code || 0;

    unless ($response->is_success) {
        $LAST_ERROR = 'FYTA API HTTP ' . ($response->code || '?');
        return undef;
    }

    my $json;
    eval { $json = decode_json($response->decoded_content); };
    if ($@) {
        $LAST_ERROR = 'Ungültige JSON-Antwort der FYTA API';
        return undef;
    }
    return $json;
}

sub get_plants
{
    my ($token) = @_;
    my $json = api_get($token, "$BASE_URL/api/user-plant");
    return undef unless ref($json) eq 'HASH';
    return undef unless ref($json->{plants}) eq 'ARRAY';
    return $json->{plants};
}

sub get_plant
{
    my ($token, $plant_id) = @_;
    return undef unless defined $plant_id;
    return undef unless $plant_id =~ /^\d+$/;
    return api_get($token, "$BASE_URL/api/user-plant/$plant_id");
}

sub get_plant_details
{
    my ($token, $plant_id) = @_;
    my $json = get_plant($token, $plant_id);
    return undef unless ref($json) eq 'HASH';
    return undef unless ref($json->{plant}) eq 'HASH';
    my $plant = $json->{plant};
    my $measurements = $plant->{measurements} || {};
    return {
        id => $plant->{id}, name => $plant->{nickname}, garden => _nested_value($plant, qw(garden name)),
        sensor => _nested_value($plant, qw(sensor id)), sensor_type => _sensor_type($plant->{sensor}),
        sensor_type_id => _nested_value($plant, qw(sensor sensor_type_id)),
        device_type => _nested_value($plant, qw(sensor device_type)),
        sensor_version => _nested_value($plant, qw(sensor version)), received => $plant->{received_data_at},
        temperature => _measurement_current($measurements, 'temperature'), moisture => _measurement_current($measurements, 'moisture'),
        light => _measurement_current($measurements, 'light'), salinity => _measurement_current($measurements, 'salinity'),
        air_humidity => _measurement_current($measurements, 'air_humidity'), ph => _measurement_current($measurements, 'ph'),
        battery => $measurements->{battery}, nutrients_status => _nested_value($measurements, qw(nutrients status)),
        temperature_status => _nested_value($measurements, qw(temperature status)),
        moisture_status => _nested_value($measurements, qw(moisture status)),
        light_status => _nested_value($measurements, qw(light status)),
        salinity_status => _nested_value($measurements, qw(salinity status))
    };
}

sub _sensor_type
{
    my ($sensor) = @_;
    return 'Unbekannt' unless ref($sensor) eq 'HASH';
    my @keys = qw(model model_name product product_name type sensor_type generation hardware_generation name);
    my @parts;
    for my $key (@keys) {
        next unless exists $sensor->{$key}; next if ref($sensor->{$key});
        my $value = $sensor->{$key}; next unless defined $value && length $value; push @parts, $value;
    }
    return join(' ', @parts) if @parts;
    my $type_id = $sensor->{sensor_type_id}; my $device_type = $sensor->{device_type};
    return "FYTA Typ $type_id" if defined $type_id && $type_id ne '';
    return "FYTA Gerätetyp $device_type" if defined $device_type && $device_type ne '';
    return 'Unbekannt';
}

sub _measurement_current
{
    my ($measurements, $name) = @_;
    return undef unless ref($measurements) eq 'HASH';
    return undef unless ref($measurements->{$name}) eq 'HASH';
    return _nested_value($measurements->{$name}, qw(values current));
}

sub _nested_value
{
    my ($node, @path) = @_;
    for my $key (@path) { return undef unless ref($node) eq 'HASH'; return undef unless exists $node->{$key}; $node = $node->{$key}; }
    return $node;
}

1;
