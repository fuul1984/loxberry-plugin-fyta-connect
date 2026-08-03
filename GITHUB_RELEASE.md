# Release 1.0.3 veröffentlichen

1. Alle Dateien dieses Quellpakets in den `main`-Branch hochladen und vorhandene Dateien ersetzen.
2. Kontrollieren, dass `plugin.cfg` und `release.cfg` jeweils `VERSION=1.0.3` enthalten.
3. Unter **Releases** einen neuen Release mit dem neuen Tag `v1.0.3` anlegen.
4. Der Workflow **Build LoxBerry release** erzeugt automatisch `FYTA_Connect_v1.0.3.zip` und hängt es an den Release.
5. Nach Abschluss des Workflows muss das Asset unter dem Release sichtbar sein.
6. Auf einem LoxBerry mit Version 1.0.2 auf **Auf neue Updates prüfen** klicken. Version 1.0.3 sollte angeboten werden.

Wichtig: Beim Erstellen des Tags müssen Tag, `plugin.cfg` und `release.cfg` dieselbe Version tragen.
