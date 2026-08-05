# FYTA Connect v1.5.0

## Highlights

- **Update-sichere Konfiguration:** Token, Miniserver, UDP-Port, Intervall und Pluginstatus bleiben bei Updates erhalten.
- **Miniserver-Dropdown:** Auswahl direkt aus den im LoxBerry hinterlegten Miniservers.
- **Aktiv/Deaktiv auf der Startseite:** Automatische Abfragen und UDP-Versand lassen sich sofort pausieren.
- **Klare Betriebsanzeige:** „Betriebsbereit“, „Kein Token gewählt“, „Kein Miniserver gewählt“ oder „Plugin deaktiviert“.
- Neue Konfigurationswerte werden bei Upgrades ergänzt, ohne vorhandene Werte zu überschreiben.

## Upgrade-Hinweis

Beim Update auf 1.5.0 wird die bestehende `fyta.cfg` vor der Installation gesichert, danach wiederhergestellt und nur um fehlende Standardschlüssel ergänzt.
