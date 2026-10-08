# FYTA Connect v1.9.5

## GitHub-Release-Titel
FYTA Connect v1.9.5 – UDP-Änderungserkennung und Synchronisationsstatus

## Release-Beschreibung
- Neues UDP-Sendeverhalten: immer alle Werte oder nur geänderte Werte.
- Bisheriges Verhalten bleibt nach dem Update Standard.
- Änderungszustand wird pro Ziel und Systemstart verwaltet.
- Heartbeat bleibt von der Änderungsfilterung ausgenommen.
- Dashboard: letzte UDP-Übertragung und nächster Scheduler-Termin getrennt angezeigt.
- Bestehende Konfiguration und FYTA-Zugangsdaten werden beim Update beibehalten.

## Release-Checkliste
- Tag: `v1.9.5`
- ZIP: `FYTA_Connect_v1.9.5.zip`
- AutoUpdate: `plugin.cfg` verweist weiterhin auf die bestehenden release.cfg-/prerelease.cfg-Adressen.
- Auf dem LoxBerry zu prüfen: FYTA-API, Cron, Worker-Lock, UDP an Loxone, Neustart, beide Sendemodi, Smartphone-UI und Update aus v1.9.0.

## Wiki-Ergänzung: UDP-Sendeverhalten
Unter Einstellungen → UDP-Ausgabe kann zwischen »Immer alle Werte senden« und »Nur geänderte Werte senden« gewählt werden. Bei Systemneustart oder Wechsel des UDP-Ziels werden die ausgewählten Werte erneut gesendet. Der Heartbeat wird bei jedem Synchronisationslauf gesendet.
