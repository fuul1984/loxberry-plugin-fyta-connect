package fyta_api;

use strict;
use warnings;

use LWP::UserAgent;
use JSON qw(decode_json);

my $BASE_URL = 'https://web.fyta.de';

sub _ua
{
    my $ua = LWP::UserAgent->new;

    $ua->timeout(20);
    $ua->agent(
        'Mozilla/5.0 (X11; Linux x86_64) '
        . 'AppleWebKit/537.36 Chrome/150.0'
    );

    $ua->default_header(
        'Accept'          => 'application/json, text/plain, */*',
        'Referer'         => 'https://web.fyta.de/',
        'Accept-Language' => 'de-CH,de;q=0.9,en-US;q=0.8,en;q=0.7'
    );

    return $ua;
}

sub api_get
{
    my ($token, $url) = @_;

    return undef unless defined $token && length $token;
    return undef unless defined $url   && length $url;

    my $ua = _ua();

    my $response = $ua->get(
        $url,
        'Authorization' => "Bearer $token"
    );

    print 'HTTP: ' . $response->status_line . "\n";

    unless ($response->is_success) {
        print $response->decoded_content . "\n";
        return undef;
    }

    my $json;

    eval {
        $json = decode_json($response->decoded_content);
    };

    if ($@) {
        warn "Ungültige JSON-Antwort von $url: $@\n";
        return undef;
    }

    return $json;
}

sub get_plants
{
    my ($token) = @_;

    my $json = api_get(
        $token,
        "$BASE_URL/api/user-plant"
    );

    return undef unless ref($json) eq 'HASH';
    return undef unless ref($json->{plants}) eq 'ARRAY';

    return $json->{plants};
}

sub get_plant
{
    my ($token, $plant_id) = @_;

    return undef unless defined $plant_id;
    return undef unless $plant_id =~ /^\d+$/;

    return api_get(
        $token,
        "$BASE_URL/api/user-plant/$plant_id"
    );
}

sub get_plant_details
{
    my ($token, $plant_id) = @_;

    my $json = get_plant($token, $plant_id);

    return undef unless ref($json) eq 'HASH';
    return undef unless ref($json->{plant}) eq 'HASH';

    my $plant        = $json->{plant};
    my $measurements = $plant->{measurements} || {};

    return {
        id          => $plant->{id},
        name        => $plant->{nickname},
        garden      => _nested_value($plant, qw(garden name)),
        sensor      => _nested_value($plant, qw(sensor id)),
        received    => $plant->{received_data_at},

        temperature => _measurement_current(
            $measurements, 'temperature'
        ),
        moisture => _measurement_current(
            $measurements, 'moisture'
        ),
        light => _measurement_current(
            $measurements, 'light'
        ),
        salinity => _measurement_current(
            $measurements, 'salinity'
        ),
        air_humidity => _measurement_current(
            $measurements, 'air_humidity'
        ),
        ph => _measurement_current(
            $measurements, 'ph'
        ),

        battery         => $measurements->{battery},
        nutrients_status =>
            _nested_value($measurements, qw(nutrients status)),

        temperature_status =>
            _nested_value($measurements, qw(temperature status)),
        moisture_status =>
            _nested_value($measurements, qw(moisture status)),
        light_status =>
            _nested_value($measurements, qw(light status)),
        salinity_status =>
            _nested_value($measurements, qw(salinity status))
    };
}

sub _measurement_current
{
    my ($measurements, $name) = @_;

    return undef unless ref($measurements) eq 'HASH';
    return undef unless ref($measurements->{$name}) eq 'HASH';

    return _nested_value(
        $measurements->{$name},
        qw(values current)
    );
}

sub _nested_value
{
    my ($node, @path) = @_;

    for my $key (@path) {
        return undef unless ref($node) eq 'HASH';
        return undef unless exists $node->{$key};

        $node = $node->{$key};
    }

    return $node;
}

1;