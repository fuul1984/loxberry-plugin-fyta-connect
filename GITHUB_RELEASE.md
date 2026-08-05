# FYTA Connect v1.6.0

## Release-Technik

- GitHub Actions erzeugt beim Tag `v1.6.0` automatisch das installierbare Asset `FYTA_Connect_v1.6.0.zip`.
- Das Paket enthält `fyta_connect/plugin.cfg` an der von LoxBerry erwarteten Position.
- Versionsnummer, Tag und AutoUpdate-URL werden vor dem Build geprüft.
- Die aktive `fyta.cfg` ist nicht im Installationspaket enthalten und kann bei einem Update daher nicht überschrieben werden.
- Bei einer Erstinstallation legt `postinstall.sh` die Standardkonfiguration an.

## Veröffentlichung

1. Inhalt dieses Repositorys in den Branch `main` übernehmen.
2. Commit erstellen.
3. Tag `v1.6.0` veröffentlichen.
4. Unter **Actions** den Lauf `Build LoxBerry Release` prüfen.
5. Im Release muss danach `FYTA_Connect_v1.6.0.zip` zusätzlich zu den beiden GitHub-Quellarchiven erscheinen.
