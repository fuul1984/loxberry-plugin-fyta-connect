# FYTA Connect für LoxBerry

Integration von FYTA-Pflanzensensoren in LoxBerry und Übertragung ausgewählter Messwerte per UDP an Loxone.

## Version

1.9.5. Versionsangabe und AutoUpdate-Konfiguration stehen in `plugin.cfg`.

## Installation

Für die Installation über die LoxBerry-Pluginverwaltung das **Installations-ZIP** aus den GitHub Releases verwenden, **nicht** das von GitHub automatisch erzeugte Source-Code-ZIP.

## GitHub Release

- Tag: `v1.9.5`
- Asset: `FYTA_Connect_v1.9.5.zip`
- AutoUpdate-Metadaten: `release.cfg` und `prerelease.cfg` im Wurzelverzeichnis des `main`-Branches

## Funktionen

- Periodische Synchronisation mit FYTA
- Auswahl der per UDP gesendeten Sensorwerte
- UDP-Sendeverhalten: alle oder nur geänderte Werte
- Statusanzeige und Logging

## Hinweise

Bestehende Einstellungen bleiben bei Updates erhalten. Die Wiki wird mit diesem Release nicht geändert.

Der Stand 1.9.5 muss vor Veröffentlichung als Stable auf einer realen LoxBerry-Installation getestet werden.
