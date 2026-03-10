# Doxology Manager

A small FastAPI application for planning church services and managing a hymn/song library. It serves a calendar UI rendered with Jinja2/FullCalendar and exposes JSON endpoints for songs and services.

## Features
- Monthly calendar with service events (time, preacher, leader, title, notes)
- Create/edit service details via HTML forms
- Simple song library: add and list songs with duplicate checks
- JSON endpoints that power the calendar and enable lightweight integrations
- Alembic migrations and Dockerized Postgres for development

## Tech Stack
- Backend: FastAPI, Starlette, SQLAlchemy 2.x
- Templates/Static: Jinja2 + FullCalendar (CDN), vanilla JS/CSS
- DB: PostgreSQL (via Docker Compose), configurable with `DATABASE_URL`
- Migrations: Alembic

## Directory Layout
```
src/
  main.py               # FastAPI app + routers + static mount
  config.py             # DATABASE_URL management
  routers/pages.py      # Jinja-rendered pages (calendar, forms)
  api/routes/           # JSON APIs: /songs, /api/services
  db/
    base.py             # engine, SessionLocal, Base, get_db()
    models.py           # Song, Service, ServiceSong
    crud.py             # basic CRUD helpers
  static/               # JS/CSS for calendar/UI
  templates/            # Jinja templates (calendar, service form/detail)
frontend/               # optional prototype client (songs only)
migrations/             # Alembic env + revisions
```

## Quickstart (Local Dev)
Prereqs: Python 3.12+, Docker, Docker Compose.

1) Start PostgreSQL
```
docker compose up -d
```

2) Create a virtualenv and install deps
```
python -m venv dm_venv
./dm_venv/Scripts/Activate.ps1   # PowerShell on Windows
pip install -r requirements.txt
```

3) Configure database URL (optional if using compose defaults)
- PowerShell (Windows):
```
$env:DATABASE_URL = "postgresql+psycopg2://doxology:doxology@localhost:5432/doxology_db"
```
- Bash (macOS/Linux):
```
export DATABASE_URL=postgresql+psycopg2://doxology:doxology@localhost:5432/doxology_db
```

4) Apply migrations
```
alembic upgrade head
```

5) Run the app
```
uvicorn src.main:app --reload
```
Visit: http://127.0.0.1:8000/ (calendar UI)

## Using the App
- Calendar: Click a day to go to the new-service form. Click a service event to view details, then edit if needed.
- Services form fields: date, time, preacher, leader, sermon title, notes.
- Songs: maintained via JSON API or the simple `frontend/` prototype (optional).

## API Endpoints
- Songs
  - `GET /songs/` → `[ { id, title, hymn_number, misc } ]`
  - `POST /songs/` with JSON body:
    ```json
    { "title": "AMAZING GRACE", "hymn_number": 23, "misc": "optional" }
    ```
    On conflict (duplicate title or hymn_number) returns 409 with a message.

- Services (for calendar)
  - `GET /api/services` → array of FullCalendar events like:
    ```json
    {
      "id": 1,
      "start": "2026-03-10",
      "extendedProps": {
        "time": "19:30",
        "preacher": "Name",
        "leader": "Name",
        "title": "Sermon Title",
        "notes": "Optional notes"
      }
    }
    ```

## Database & Migrations
- Configure connection via `DATABASE_URL` or edit `docker-compose.yml`.
- Common Alembic commands:
```
# create a new revision from model changes
alembic revision --autogenerate -m "your message"

# apply latest
alembic upgrade head

# rollback one
alembic downgrade -1
```

## Development Notes
- CORS is wide-open in `src/main.py` for development; restrict in production.
- `dev.db` exists in the repo but the app uses PostgreSQL by default; you can remove it if not needed.
- The `frontend/` folder is a small static prototype for `/songs/` and is not required for normal use.

## Troubleshooting
- Connection refused to Postgres: ensure `docker compose up -d` is running and port 5432 is free.
- Alembic URL mismatch: `migrations/env.py` reads `DATABASE_URL`; verify your environment variable.
- Calendar not showing events: confirm you created services and that `/api/services` responds 200.

## License
Not specified.
