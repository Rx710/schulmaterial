# Schulmaterial App

Dieses Projekt stellt eine einfache Flask-Anwendung dar, die Lehr- und Lernmaterialien verwaltet. Die Anwendung kann mit Docker gestartet werden.

## Docker-Start

Führe folgenden Befehl aus, um die Anwendung zu starten:

```bash
docker-compose up
```

Falls der Standard-Port `5000` auf deinem System bereits belegt ist, kannst du einen anderen Host-Port angeben, indem du die Umgebungsvariable `WEB_PORT` setzt:

```bash
WEB_PORT=5001 docker-compose up
```

So wird die Anwendung innerhalb des Containers weiterhin auf Port `5000` laufen, ist aber über den gewählten Host-Port erreichbar.
## Nutzung

Nach dem Start erreichst du die Anwendung unter `http://localhost:WEB_PORT` (standardmäßig `5000`).
Die Startseite ist nur nach erfolgreichem Login verfügbar. Melde dich daher zuerst unter `/login` an.

Auf der Startseite kannst du Materialien nach Text durchsuchen oder über die Buttons nach Themen oder Tags filtern. Mit dem Stern neben einem Material lässt es sich zu deinen Favoriten hinzufügen. Alle gespeicherten Favoriten findest du über den Link "Favoriten" in der Navigation oder unter `/favoriten`.

Beim ersten Start der Anwendung werden automatisch zwei Testnutzer erzeugt:
