# Vehicle Maintenance App

## Run the database (Postgres with Docker)

```bash
cd backend/db/init
docker compose up -d
```

To stop it later:

```bash
docker compose down
```

Database details:

- Host: `127.0.0.1`
- Port: `5432`
- Database: `app_db`
- User: `app`
- Password: `app_pw`

## Run the backend (FastAPI)

```bash
cd backend
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
