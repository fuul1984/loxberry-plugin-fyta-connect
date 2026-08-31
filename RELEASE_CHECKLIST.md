# FYTA Connect v1.9.0 – Release-Checkliste

- [x] Letzten offiziellen GitHub-Release geprüft: v1.7.0
- [x] Teststand 1.8.84 als Basis verwendet
- [x] Version zentral in `plugin.cfg` auf 1.9.0 gesetzt
- [x] Keine Version separat in CGI-Dateien hardcodiert
- [x] Changelog 1.7.0 → 1.9.0 erstellt
- [x] README aktualisiert
- [x] GitHub-Release-Beschreibung erstellt
- [x] DokuWiki-Seite aktualisiert
- [x] `release.cfg` auf v1.9.0 aktualisiert
- [x] `prerelease.cfg` auf v1.9.0 aktualisiert
- [x] Installations-ZIP ohne `fyta.cfg` erstellt
- [x] Update-Sicherung für `fyta.cfg`, `auth.json` und `.auth.key` vorhanden
- [x] Worker-Locking vorhanden
- [x] Heartbeat- und Aktuell-Logik im Code vorhanden
- [x] UTF-8-Pfad in CGI/Worker/Scheduler/Logging vorhanden
- [x] Smartphone-/Button-Fixes aus 1.8.82–1.8.84 enthalten
- [x] Git-Tag vorbereitet: `v1.9.0`
- [x] GitHub-Release-Titel vorbereitet: `FYTA Connect v1.9.0`

## Vor Veröffentlichung auf echtem LoxBerry nochmals testen

- [ ] Neuinstallation
- [ ] Update von offizieller v1.7.0
- [ ] Einstellungen speichern/laden
- [ ] FYTA-Login und automatischer Re-Login
- [ ] Scheduler und Worker
- [ ] paralleler Start / Locking
- [ ] UDP an Miniserver
- [ ] `FYTA_Heartbeat=1/0`
- [ ] `FYTA_<Pflanze>_Aktuell=1/0`
- [ ] Sonderzeichen/Umlaute im UI und Log
- [ ] Smartphone-Ansicht
- [ ] AutoUpdate nach veröffentlichtem GitHub-Release
