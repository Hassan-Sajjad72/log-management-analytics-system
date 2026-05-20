# Flask Backend

## Purpose

This backend connects the PostgreSQL log analytics database with a Flask-based dashboard and JSON APIs.

## Tech Stack

- Python
- Flask
- PostgreSQL
- psycopg2
- python-dotenv
- Jinja templates

## Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```


## Create `.env`:

DB_HOST=localhost
DB_NAME=log_management
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_PORT=5432

## Run:

```bash
python app.py
```

## Open:
http://127.0.0.1:5000

## Pages:

- /
- /logs
- /analytics
- /benchmarks
- /techniques
- /services

## APIs

- /api/health
- /api/logs
- /api/logs/<log_db>
- /api/services
- /api/analytics/summary
- /api/analytics/errors-by-service
- /api/analytics/endpoint-latency