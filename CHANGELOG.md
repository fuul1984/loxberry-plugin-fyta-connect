# Changelog

## 1.5.1 – 2026-08-05

- Miniserver-Erkennung für unterschiedliche Rückgabeformen von LoxBerry 4 korrigiert.
- Gespeicherter Miniserver wird zuerst über die Miniserver-Nummer und anschließend über IP/Hostname wiedergewählt.
- Falls keine bisherige Auswahl passt, wird automatisch der erste konfigurierte Miniserver ausgewählt.
- Miniserver-Name wird zusätzlich in der Plugin-Konfiguration gespeichert.
- GitHub-Release-Workflow auf Version 1.5.1 vorbereitet.

## 1.5.0 – 2026-08-05

- Benutzereinstellungen bleiben bei Plugin-Updates erhalten.
- Upgrade-Sicherung und Wiederherstellung für `fyta.cfg`.
- Neue Konfigurationsschlüssel werden automatisch ergänzt, bestehende Werte nicht überschrieben.
- Miniserver-Auswahl direkt aus den LoxBerry-Systemeinstellungen.
- Plugin kann auf der Startseite aktiviert oder deaktiviert werden.
- Startseite zeigt „Kein Token gewählt“ und fehlende Miniserver-Konfiguration deutlich an.
- Token, UDP-Ziel, Port, Intervall, Status und Logs bleiben bei Updates erhalten.

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
