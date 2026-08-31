# FYTA Connect v1.9.0

FYTA Connect v1.9.0 fasst die seit der letzten offiziellen Version **v1.7.0** getesteten Weiterentwicklungen zu einem neuen stabilen Release zusammen.

## Highlights

- sicherere FYTA-Anmeldung mit getrenntem, geschütztem Auth-Speicher
- automatischer Re-Login bei abgelaufenem bzw. abgewiesenem Access-Token
- Worker-Locking gegen parallele Cron-/manuelle Läufe
- robustere Scheduler- und Reboot-Fehlerbehandlung
- globaler UDP-Heartbeat `FYTA_Heartbeat=1/0`
- optionaler Pflanzenstatus `FYTA_<Pflanze>_Aktuell=1/0`
- konfigurierbare Aktualitätsgrenze pro Pflanze/Sensor
- vollständig korrigierte UTF-8-Ausgabe in CGI, Worker, Scheduler, Status und Logging
- responsive Smartphone-Darstellung
- gut lesbare Buttons in allen Zuständen
- vereinfachte Passwort-/Token-Oberfläche ohne unnötige „Anzeigen“-Buttons
- zentrale Versionsanzeige aus `plugin.cfg`

## Update-Sicherheit

Ein direktes Update von v1.7.0 auf v1.9.0 ist vorgesehen. Bestehende FYTA-, Miniserver-, UDP-, Intervall-, Plugin- und Sensoreinstellungen bleiben erhalten. `fyta.cfg` und geschützte Auth-Daten werden beim Upgrade gesichert und wiederhergestellt.

## Loxone / UDP

Beispiele:

```text
FYTA_Frangipani_Temperature=22.4
FYTA_Frangipani_Moisture=38
FYTA_Frangipani_Aktuell=1
FYTA_Heartbeat=1
```

Analoge Werte werden numerisch übertragen; digitale Zustände als `1` und `0`.

## Release-Daten

- Tag: `v1.9.0`
- Titel: `FYTA Connect v1.9.0`
- Asset: `FYTA_Connect_v1.9.0.zip`
- Kanal: Stable / Release

Die vollständige Änderungsliste seit v1.7.0 befindet sich in `CHANGELOG.md`.
