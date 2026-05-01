# Vehicle Maintenance App

## Configuration (environment variables)

You can now configure backend and database settings with environment variables.
Copy `.env.example` to `.env` and adjust values as needed.

Backend (`backend/app/database.py`, `backend/app/main.py`):

- `DATABASE_URL` (preferred, full connection string)
- `DB_USER` (default: `app`)
- `DB_PASSWORD` (default: `app_pw`)
- `DB_HOST` (default: `localhost`)
- `DB_PORT` (default: `5432`)
- `DB_NAME` (default: `app_db`)
- `CORS_ALLOWED_ORIGINS` (comma-separated, default: `http://localhost:4200,http://127.0.0.1:4200`)

Database container (`backend/db/init/docker-compose.yml`):

- `POSTGRES_USER` (default: `app`)
- `POSTGRES_PASSWORD` (default: `app_pw`)
- `POSTGRES_DB` (default: `app_db`)
- `POSTGRES_PORT` (default: `5432`)

Frontend API base URL:

- Development uses `frontend/src/environments/environment.development.ts`
- Production uses `frontend/src/environments/environment.ts`

## Production Docker behavior

When you run `docker compose -f docker-compose.prod.yml up -d --build`, a `seed` service
now runs `backend/seed.py` automatically before the backend starts.

## Run the database (Postgres with Docker)

```bash
cp .env.example .env  # first time only
cd backend/db/init
docker compose up -d
```

To stop it later:

```bash
docker compose down
```

Database defaults:

- Host: `127.0.0.1`
- Port: `5432`
- Database: `app_db`
- User: `app`
- Password: `app_pw`

## Run the backend (FastAPI)

```bash
cd backend
set -a
source ../.env
set +a
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend will run at `http://127.0.0.1:8000`.

## Run the frontend (Angular)

In a second terminal:

```bash
cd frontend
npm install
npm start
```

Frontend will run at `http://localhost:4200`.
