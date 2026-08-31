# FYTA Connect für LoxBerry

**Version:** 1.9.0  
**Status:** Stable / Release  
**Minimum LoxBerry:** 4.0.0

FYTA Connect liest Pflanzen- und Sensorwerte über die FYTA-Webschnittstelle und stellt sie Loxone insbesondere per UDP zur Verfügung.

## Funktionen

- Automatische Erkennung der verfügbaren FYTA-Pflanzen und Sensordaten
- Numerische UDP-Ausgabe an einen in LoxBerry konfigurierten Loxone Miniserver
- Unterstützte Werte werden dynamisch aus den verfügbaren FYTA-Daten übernommen
- Konfigurierbares Abrufintervall über LoxBerry Cron → Scheduler → Worker
- Worker-Locking gegen parallele Synchronisationen
- Dashboard mit Status, letztem erfolgreichen Lauf und Synchronisationsinformationen
- Manueller Sync und UDP-Test
- Globaler Heartbeat `FYTA_Heartbeat=1/0`
- Optionaler Aktualitätswert pro Pflanze `FYTA_<Pflanze>_Aktuell=1/0`
- Update-sichere Plugin-, Miniserver-, UDP-, Intervall- und Sensoreinstellungen
- Geschützter Auth-Speicher für Passwort und Token-Daten
- Responsive deutsche Benutzeroberfläche für Desktop und Smartphone
- UTF-8-sichere Oberfläche und Protokollierung

## UDP-Format

Beispiele:

```text
FYTA_Frangipani_Temperature=22.4
FYTA_Frangipani_Moisture=38
FYTA_Frangipani_Aktuell=1
FYTA_Heartbeat=1
```

Analoge Werte werden numerisch übertragen. Boolesche Zustände werden als `1` oder `0` gesendet. Falls für einen bekannten Messwert kein gültiger numerischer Wert verfügbar ist, kann der bestehende Fallback `-9999` verwendet werden.

### Heartbeat

- `FYTA_Heartbeat=1`: Ein FYTA-Lauf konnte die Daten erfolgreich verarbeiten und der Heartbeat wurde per UDP gesendet.
- `FYTA_Heartbeat=0`: Bei einem fehlgeschlagenen Lauf versucht das Plugin, einen Fehler-Heartbeat zu senden.

Der Heartbeat ist vom Pflanzenwert `Aktuell` zu unterscheiden: Eine Pflanze kann veraltete Sensordaten haben, obwohl das Plugin selbst erfolgreich arbeitet.

## Installation

Das Release-ZIP `FYTA_Connect_v1.9.0.zip` über den LoxBerry Plugin Manager installieren. Anschließend in den Einstellungen FYTA-Zugang, Miniserver, UDP-Port und Intervall konfigurieren.

## Update von 1.7.0

Das Update ist so ausgelegt, dass vorhandene Einstellungen erhalten bleiben. `fyta.cfg` sowie geschützte Auth-Daten werden vor dem Upgrade gesichert und danach wiederhergestellt. Neue Schlüssel werden mit Defaults ergänzt, ohne bestehende Werte zu überschreiben.

## AutoUpdate

Der Stable-Kanal verwendet `release.cfg`. Für v1.9.0 zeigt die Datei auf:

```text
https://github.com/fuul1984/loxberry-plugin-fyta-connect/releases/download/v1.9.0/FYTA_Connect_v1.9.0.zip
```

## Release

Git-Tag: `v1.9.0`  
GitHub-Release-Titel: `FYTA Connect v1.9.0`

Die vollständigen Änderungen seit der letzten offiziellen Version 1.7.0 stehen in `CHANGELOG.md`.

## Lizenz

MIT
