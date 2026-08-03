# FYTA Connect for LoxBerry

FYTA Connect reads plant measurements from the FYTA web API and sends numeric UDP messages to a Loxone Miniserver.

## Features

- Automatic plant discovery
- Temperature, moisture, light, salinity and battery values
- Configurable polling interval
- Automatic polling through the LoxBerry cron folders
- Dashboard with last run and transmission status
- Manual synchronization and UDP test
- Single plugin log capped at 1 MB
- Missing values are sent as the numeric fallback `-9999`
- Cached plant list allows fallback messages when the FYTA plant list cannot be fetched

## UDP format

```text
FYTA_Frangipani_Temperature=22
FYTA_Frangipani_Moisture=-9999
```

`-9999` means that no valid value was available.

## Installation

Install the release ZIP through the LoxBerry Plugin Manager. Configure the FYTA token, UDP target and polling interval in the plugin settings.

## Automatic GitHub releases

The included GitHub Actions workflow creates an installable ZIP and a GitHub Release whenever a tag such as `v1.0.2` is pushed. See `GITHUB_RELEASE.md`.

## License

MIT
