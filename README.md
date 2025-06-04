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
