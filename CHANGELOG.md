# Changelog

## 1.0.5 – 2026-08-04

- Miniserver-Auswahl als Dropdown aus der LoxBerry-Systemkonfiguration.
- Plugin direkt auf der Startseite aktivieren oder deaktivieren.
- Dashboard zeigt Token- und Miniserver-Konfigurationsstatus.
- Scheduler und manuelle Synchronisation respektieren den deaktivierten Zustand.
- Unvollständige Konfiguration wird klar als Warnung angezeigt.


## 1.0.3 – 2026-08-03

- LoxBerry AutoUpdate-Konfiguration für den Release-Kanal vereinheitlicht.
- Release- und Download-URLs auf Version 1.0.3 aktualisiert.
- GitHub-Workflow prüft vor dem Release die Versionen in `plugin.cfg` und `release.cfg`.
- Installierbares Plugin-ZIP wird bei einem Tag `v*` automatisch als Release-Asset erzeugt.

## 1.0.2 - 2026-08-03

- LoxBerry AutoUpdate für das öffentliche GitHub-Repository aktiviert.
- `release.cfg` und `prerelease.cfg` ergänzt.
- Release-Workflow für das installierbare ZIP angepasst.

## 1.0.1

- Send numeric fallback value `-9999` for unavailable measurements.
- Send all five fallback values when plant detail data cannot be fetched.
- Cache the last known plant list for fallback transmission when plant discovery fails.
- Show fallback-value count and warning state in the dashboard.
- Respect the configured interval after failed runs to avoid API requests every minute.
- Prepare automatic GitHub release creation on version tags.

## 1.0.0

- First stable release with LoxBerry integration, scheduler, dashboard, UDP test and logging.
