# Election Track — Admin Backend

A FastAPI backend that powers the admin/monitoring side of the Election Track
system. Election-day admins log in to view live collection progress, browse
individual field reports, check the latest GPS location of each field
officer, and export all reports to Excel.

This is the **admin-facing** counterpart to the mobile field-worker backend —
that service handles officers submitting reports and GPS pings; this service
lets admins view and export that data.

## Features

- **Admin authentication** — JWT-based login/logout for admin accounts
- **Dashboard** — collection/hand-over progress for the current and previous
  polling day, based on a configured polling date
- **Reports** — list all field reports, optionally filtered by date
- **Excel export** — download all reports as an `.xlsx` file
- **Live GPS lookup** — latest known location per field officer

## Tech stack

- **FastAPI** — web framework
- **SQLModel** / **SQLAlchemy** — ORM and database models
- **PostgreSQL** — database
- **python-jose** — JWT access tokens
- **passlib** + **bcrypt** — password hashing
- **openpyxl** — Excel (`.xlsx`) export
- **pydantic-settings** — environment-based configuration

## How it works

Admins authenticate via `POST /admin/login`, which returns a JWT access
token. That token is sent as a `Bearer` token on every subsequent request;
`get_current_admin` (in `app/core/dependencies.py`) validates it and loads
the admin from the database on each protected request.

The dashboard endpoint compares report counts/status for a configured
`POLLING_DATE` against the day before it, rather than using the server's
current date — this keeps results stable regardless of when the dashboard is
viewed.

Reports and GPS pings are read-only from this service's perspective — they're
written by the separate field-worker mobile backend and simply queried here.

## Project structure

```
backend/app/
├── main.py              # App entrypoint, router registration, CORS
├── core/
│   ├── config.py         # Environment-based settings
│   ├── security.py       # Password hashing, JWT creation
│   └── dependencies.py   # get_current_admin auth dependency
├── db/
│   └── session.py         # Database engine/session
├── models/                # SQLModel table definitions (Admin, Report, GPSPing)
├── schemas/               # Pydantic request/response schemas
└── api/
    ├── auth.py            # Login / logout
    ├── progress.py        # Dashboard stats
    ├── report.py           # Report listing
    ├── exportdata.py       # Excel export
    └── gpspings.py         # Latest GPS location per officer
```

## Setup and installation

```bash
git clone <repo-url>
cd ElectionTrackWebsite

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

cd backend
cp ../.env.example .env
# then edit backend/.env with your own SECRET_KEY, DATABASE_URL and POLLING_DATE
```

## Running the server

```bash
cd backend
uvicorn app.main:app --reload
```

The API is now available at `http://localhost:8000`, with interactive docs
at `http://localhost:8000/docs`. Tables are created automatically on
startup.

## Example usage

```bash
curl -X POST http://localhost:8000/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "yourpassword"}'
```

```bash
curl http://localhost:8000/admin/dashboard \
  -H "Authorization: Bearer <access_token>"
```

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/admin/login` | Admin login, returns a JWT access token |
| POST | `/admin/logout` | Admin logout |
| GET | `/admin/dashboard` | Collection/hand-over progress for today vs. the previous polling day |
| GET | `/admin/reports` | List field reports, optionally filtered by `report_date` |
| GET | `/admin/export-tasks` | Export all reports as an Excel file |
| GET | `/gps/latest` | Latest GPS ping per field officer |
