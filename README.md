# Videoflix

## Projektübersicht

Dies ist ein Django-Backend für das Videoflix-Projekt. Die Anwendung nutzt PostgreSQL als Datenbank, Redis für Caching/Jobs und Docker zur lokalen Entwicklung.

---

## Voraussetzungen

- Git
- Python 3.12 (für lokale Installation empfohlen)
- Docker und Docker Compose (für die Docker-Installation)
- optional: `virtualenv` oder venv-Unterstützung für Python

---

## Installation mit Docker

1. Repository klonen:

```bash
git clone https://github.com/TobiasDreifke/15_videoflix.git
cd 15_videoflix
```

2. `.env` aus der Vorlage erstellen:

- Kopiere die Datei `.env.template` nach `.env` im Projektstamm:

```powershell
copy .env.template .env
```

- Die Datei `.env` wird von `docker-compose.yml` geladen.
- Passe anschließend folgende Werte an:
  - `DB_NAME`
  - `DB_USER`
  - `DB_PASSWORD`
  - `DB_HOST=db`
  - `DB_PORT=5432`
  - `DJANGO_SUPERUSER_USERNAME`
  - `DJANGO_SUPERUSER_PASSWORD`
  - `DJANGO_SUPERUSER_EMAIL`
  - `SECRET_KEY`
  - `ALLOWED_HOSTS`
  - `CSRF_TRUSTED_ORIGINS`
  - `FRONTEND_URL`
  - `BACKEND_URL`

> Achtung: Die `.env`-Datei enthält sensible Daten. Nicht in ein öffentliches Repository einchecken.

3. Docker-Container bauen und starten:

```powershell
docker-compose up --build -d
```

4. Datenbank-Migrationen durchführen:

```powershell
docker-compose exec web python manage.py migrate
```

5. Optional: Superuser anlegen (falls noch nicht automatisch vorhanden):

```powershell
docker-compose exec web python manage.py createsuperuser
```

6. Backend aufrufen:

- `http://127.0.0.1:8000`

---

## Lokale Installation ohne Docker

1. Virtuelle Umgebung erstellen:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Abhängigkeiten installieren:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

3. `.env` konfigurieren:

- Kopiere die vorhandene `.env`-Datei oder erstelle sie neu.
- Setze die korrekten Datenbank- und Django-Werte.

4. Migrationen ausführen:

```powershell
python manage.py migrate
```

5. Superuser erstellen:

```powershell
python manage.py createsuperuser
```

6. Backend starten:

```powershell
python manage.py runserver
```

7. Backend aufrufen:

- `http://127.0.0.1:8000`

---

## Umgebungsvariablen

Die wichtigsten Variablen in `.env` sind:

- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_PASSWORD`
- `DJANGO_SUPERUSER_EMAIL`
- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_DB`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS`
- `EMAIL_USE_SSL`
- `DEFAULT_FROM_EMAIL`
- `FRONTEND_URL`
- `BACKEND_URL`

---

## Tests

Um die Django-Tests auszuführen, verwende:

```powershell
python manage.py test
```

Bei Docker:

```powershell
docker-compose exec web python manage.py test
```

---

## Hinweis

- Der Docker-Build verwendet `backend.Dockerfile` mit Python 3.12 auf Alpine Linux.
- Die Datenbank ist in `docker-compose.yml` als `postgres:latest` konfiguriert.
- Redis wird als eigener Service gestartet und steht im Container-Netzwerk unter `redis` zur Verfügung.
