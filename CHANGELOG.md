# Changelog

## 1.9.5 – 2026-10-08

- UDP-Sendeverhalten wählbar: alle Werte oder nur Änderungen; bisheriger Standard bleibt erhalten.
- Änderungsstatus pro UDP-Ziel gespeichert, nach Neustart oder Zielwechsel vollständiger Versand.
- Heartbeat wird weiterhin unabhängig vom gewählten Sendeverhalten übertragen.
- Dashboard zeigt den letzten UDP-Versand und berechnet die nächste Synchronisation anhand des Scheduler-Zeitstempels.
- Warnläufe mit erfolgreich verarbeiteten Daten aktualisieren den Erfolgszeitpunkt.
- Bestehende Einstellungen bleiben erhalten.


## 1.9.0 – 2026-08-31

### Änderungen seit der letzten offiziellen Version 1.7.0

#### Authentifizierung und Sicherheit
- FYTA-E-Mail, Passwort und API-Token werden in der Oberfläche klar getrennt behandelt.
- Das FYTA-Passwort wird nicht mehr in `fyta.cfg` gespeichert, sondern geschützt in einem separaten Auth-Speicher abgelegt.
- Auth-Datei und lokaler Schlüssel werden mit restriktiven Dateirechten gespeichert und bei Updates gesichert und wiederhergestellt.
- Access- und Refresh-Token werden vom normalen Plugin-Config getrennt verwaltet; vorhandene 1.8.x-/Legacy-Token werden übernommen.
- Bei abgelaufenem oder von FYTA abgewiesenem Access-Token kann sich das Plugin automatisch erneut anmelden, sofern FYTA-E-Mail und Passwort hinterlegt sind.
- Passwörter und vollständige Tokens werden weder im UI zurückgegeben noch im Plugin-Log ausgegeben.
- Überflüssige „Anzeigen“-Schaltflächen für Passwort und Token wurden entfernt; die Eingabefelder bleiben maskiert.

#### Scheduler, Worker und Robustheit
- Worker-Locking verhindert parallele Ausführung von Cron- und manuellen Synchronisationen.
- Der Scheduler aktualisiert den letzten erfolgreichen Lauf nur nach erfolgreicher Verarbeitung.
- Nach Reboot, temporären Netzwerkproblemen oder API-Fehlern wird beim nächsten fälligen Cron-Lauf erneut versucht.
- Ein bereits laufender Worker wird sauber erkannt und ein Parallelstart übersprungen.
- Bestehende Miniserver-, UDP-, Sensor-, Intervall-, Plugin- und Auth-Einstellungen bleiben bei Updates erhalten.

#### UDP und Loxone
- Globaler Heartbeat `FYTA_Heartbeat=1/0` für den Zustand des FYTA-Abrufs/der Verarbeitung.
- Digitaler Pflanzenwert `FYTA_<Pflanze>_Aktuell=1/0` zur Bewertung der Datenaktualität.
- Die Aktualitätsgrenze ist pro Pflanze/Sensor konfigurierbar.
- „Aktuell senden“ wird stabil an die FYTA-Pflanzen-ID gebunden; bestehende sensorbasierte Einstellungen bleiben als Fallback kompatibel.
- Boolesche Altwerte wie `true`, `1`, `yes` und `on` werden robust erkannt.
- Pflanzen-Cache dient als Fallback, damit die Auswahl auch bei vorübergehend fehlenden Metadaten erhalten bleibt.

#### UTF-8 und Logging
- UTF-8-Ausgabe im zentralen Logger korrigiert.
- Mojibake wie `lÃ¤uft` oder `â` wird vermieden.
- Statusdatei, Worker-Ausgabe, Scheduler und CGI-Ausgabe verwenden konsistent UTF-8.
- Umlaute, `ß`, Gedankenstrich und weitere sichtbare Sonderzeichen werden korrekt dargestellt.

#### Oberfläche und Mobile
- CGI-Oberflächen für Smartphones und schmale Displays überarbeitet.
- Karten, Navigation, Statusfelder, Formulare, Tabellen und Aktionsbuttons reagieren auf kleinere Bildschirmbreiten.
- Sensor-Aktualität wird mobil als lesbare Kartenansicht statt als gequetschte Tabelle dargestellt.
- Buttons und Navigation sind in Normal-, Hover-, Focus-, Active- und Disabled-Zuständen kontrastreich und lesbar.
- „Aktuell senden“ verwendet einen eigenen stabilen Toggle statt geerbter Checkbox-Darstellung.
- Schaltflächen zum Aktivieren bzw. Deaktivieren aller `Aktuell`-Werte ergänzt.
- Versionsanzeige wird zentral aus `plugin.cfg` ermittelt und in den CGI-Seiten einheitlich verwendet.

### Update-Hinweise
- Direktes Update von 1.7.0 auf 1.9.0 ist vorgesehen.
- `fyta.cfg` wird vor dem Upgrade gesichert und danach wiederhergestellt.
- Geschützte Auth-Daten werden ebenfalls update-sicher behandelt.
- Neue Konfigurationswerte werden nur ergänzt; bestehende Werte werden nicht überschrieben.

## Entwicklungsstände zwischen 1.7.0 und 1.9.0

Die Versionen 1.8.x waren interne bzw. getestete Entwicklungsstände auf dem Weg zu 1.9.0. Ihre Änderungen sind in der obigen offiziellen 1.9.0-Zusammenfassung konsolidiert.

## 1.7.0 – 2026-08-05
- Miniserver-Dropdown liest die LoxBerry-4-Felder `Name` und `IPAddress` korrekt.
- Gespeicherter Miniserver wird über Nummer oder IP automatisch wieder ausgewählt.
- Falls noch keine Auswahl gespeichert ist, wird der erste konfigurierte Miniserver vorausgewählt.
- Plugin kann direkt auf der Startseite aktiviert oder deaktiviert werden.
- Startseite zeigt deutlich „Kein Token gewählt“ beziehungsweise „Kein Miniserver gewählt“.
- Konfiguration wird bei Updates gesichert und wiederhergestellt; fehlende Schlüssel werden nur ergänzt.
- Release-Workflow erstellt das installierbare LoxBerry-ZIP automatisch.

## 1.5.1 – 2026-08-05
- Miniserver-Erkennung für unterschiedliche Rückgabeformen von LoxBerry 4 korrigiert.
- Gespeicherter Miniserver wird zuerst über die Miniserver-Nummer und anschließend über IP/Hostname wiedergewählt.
- Falls keine bisherige Auswahl passt, wird automatisch der erste konfigurierte Miniserver ausgewählt.
- Miniserver-Name wird zusätzlich in der Plugin-Konfiguration gespeichert.

## 1.5.0 – 2026-08-05
- Benutzereinstellungen bleiben bei Plugin-Updates erhalten.
- Upgrade-Sicherung und Wiederherstellung für `fyta.cfg`.
- Neue Konfigurationsschlüssel werden automatisch ergänzt, bestehende Werte nicht überschrieben.
- Miniserver-Auswahl direkt aus den LoxBerry-Systemeinstellungen.
- Plugin kann auf der Startseite aktiviert oder deaktiviert werden.

## 1.0.3 – 2026-08-03
- LoxBerry AutoUpdate-Konfiguration für den Release-Kanal vereinheitlicht.
- GitHub-Workflow prüft Versionen und erzeugt ein installierbares Release-ZIP.

## 1.0.2 – 2026-08-03
- LoxBerry AutoUpdate für das öffentliche GitHub-Repository aktiviert.
- `release.cfg` und `prerelease.cfg` ergänzt.

## 1.0.1
- Numerischer Fallback `-9999` für nicht verfügbare Messwerte.
- Pflanzen-Cache und erweiterte Statusanzeige ergänzt.

## 1.0.0
- Erste stabile Version mit LoxBerry-Integration, Scheduler, Dashboard, UDP-Test und Logging.
