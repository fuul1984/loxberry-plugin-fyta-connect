# Changelog

## 1.0.1

- Send numeric fallback value `-9999` for unavailable measurements.
- Send all five fallback values when plant detail data cannot be fetched.
- Cache the last known plant list for fallback transmission when plant discovery fails.
- Show fallback-value count and warning state in the dashboard.
- Respect the configured interval after failed runs to avoid API requests every minute.
- Prepare automatic GitHub release creation on version tags.

## 1.0.0

- First stable release with LoxBerry integration, scheduler, dashboard, UDP test and logging.
