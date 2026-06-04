# Setup Guide

## PostgreSQL setup

1. Install PostgreSQL (Windows installer) from https://www.postgresql.org/download/windows/.
2. During install, set a password for the `postgres` superuser and remember the port (default `5432`).
3. Create the project database and a user (example):

```sql
-- run in psql or pgAdmin query tool
CREATE DATABASE log_management;
CREATE USER log_user WITH PASSWORD 'change_me';
GRANT ALL PRIVILEGES ON DATABASE log_management TO log_user;
```

4. Copy `.env.example` to `.env` and set your database credentials before running the generator.

Note: there are two example env files:

- `.env.example` at the repository root — used by scripts and generators.
- `backend/.env.example` — used by the Flask backend. Copy the appropriate file to `.env` or `backend/.env`.

## pgAdmin setup

1. Install pgAdmin if you prefer a GUI.
2. Add a new server connection pointing at `localhost:5432` with user `postgres` (or `log_user`).
3. Use the Query Tool or the Import panels to run schema files under `sql/schema/`.

## venv setup (Python)

From the project root — Windows and POSIX examples:

# Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

# macOS / Linux (bash)
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell execution policy blocks activation, run (as admin):

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## Running scripts

1. Ensure the DB is created and apply the master schema file first. Use the database role you created (example `log_user`):

Windows PowerShell:

```powershell
psql -h localhost -U log_user -d log_management -f sql/schema/00_create_all_tables.sql
```

macOS / Linux:

```bash
PGPASSWORD="your_password" psql -h localhost -U log_user -d log_management -f sql/schema/00_create_all_tables.sql
```

2. Seed reference tables with the master seed file:

Windows PowerShell:

```powershell
psql -h localhost -U log_user -d log_management -f sql/seed/00_seed_all.sql

# Or run individual seed files (if you prefer explicit ordering):
psql -h localhost -U log_user -d log_management -f sql/seed/seed_users.sql
psql -h localhost -U log_user -d log_management -f sql/seed/seed_services.sql
psql -h localhost -U log_user -d log_management -f sql/seed/seed_servers.sql
psql -h localhost -U log_user -d log_management -f sql/seed/seed_log_levels.sql
psql -h localhost -U log_user -d log_management -f sql/seed/seed_error_categories.sql
psql -h localhost -U log_user -d log_management -f sql/seed/seed_api_endpoints.sql
```

3. Generate logs from the project root, with venv activated:

```powershell
python scripts/generate_logs.py
```

4. To simulate live logs during a dashboard demo, run this in a separate terminal:

```powershell
python scripts/simulate_live_logs.py
```

Optional settings:

```powershell
$env:LIVE_BATCH_SIZE=50
$env:LIVE_INTERVAL_SECONDS=2
$env:LIVE_MAX_BATCHES=0
python scripts/simulate_live_logs.py
```

5. Create the materialized views for dashboard-style analytics:

```powershell
psql -h localhost -U log_user -d log_management -f sql/schema/01_create_materialized_views.sql
```

6. After loading more logs later, refresh the summaries:

```powershell
psql -h localhost -U log_user -d log_management -f sql/schema/02_refresh_materialized_views.sql
```

7. If you run into Python module errors, ensure the virtualenv is activated and packages from `requirements.txt` are installed.

## Troubleshooting

- `psql: FATAL: password authentication failed for user "log_user"`: verify the password in your `.env` or use `PGPASSWORD` for the command.
- `cannot connect to server: Connection refused`: ensure PostgreSQL server is running and listening on the expected port (default 5432).
- Virtualenv activation blocked on Windows PowerShell: run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` as admin.
- If `psql` not found: ensure PostgreSQL bin directory is in your `PATH` or use the full path to `psql`.

## Applying Partitioning

After seeding and generating logs, apply the partitioned schema:

```powershell
psql -h localhost -U postgres -d log_management -f sql/schema/05_create_partitioned_logs.sql
```

Verify partition pruning is active by running:

```powershell
psql -h localhost -U postgres -d log_management -f sql/benchmarks/partitioning/01_partition_pruning_check.sql
```

## Backend Dashboard Setup

From the `backend/` directory:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env` using your local database credentials:

```env
DB_HOST=localhost
DB_NAME=log_management
DB_USER=postgres
DB_PASSWORD=
DB_PORT=5432
```

Run the Flask dashboard:

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Demo Checklist

Before presenting, refresh analytics summaries:

```powershell
psql -h localhost -U postgres -d log_management -f sql/schema/02_refresh_materialized_views.sql
```

Then check these pages:

- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/logs`
- `http://127.0.0.1:5000/analytics`
- `http://127.0.0.1:5000/analytics/olap`
- `http://127.0.0.1:5000/techniques`
- `http://127.0.0.1:5000/benchmarks`

And these API endpoints:

- `http://127.0.0.1:5000/api/health`
- `http://127.0.0.1:5000/api/logs?limit=5`
- `http://127.0.0.1:5000/api/analytics/daily-service-activity`
- `http://127.0.0.1:5000/api/analytics/olap/daily-totals`
