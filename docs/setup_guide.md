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

## pgAdmin setup

1. Install pgAdmin if you prefer a GUI.
2. Add a new server connection pointing at `localhost:5432` with user `postgres` (or `log_user`).
3. Use the Query Tool or the Import panels to run schema files under `sql/schema/`.

## venv setup (Python)

From the project root on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell execution policy blocks activation, run (as admin):

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## Running scripts

1. Ensure the DB is created and schema files applied. Example using psql:

```powershell
psql -h localhost -U postgres -d log_management -f sql/schema/logs.sql
```

2. Seed reference tables:

```powershell
psql -h localhost -U postgres -d log_management -f sql/seed/seed_services.sql
psql -h localhost -U postgres -d log_management -f sql/seed/seed_servers.sql
# ... other seed files
```

3. Generate logs (from project root, with venv activated):

```powershell
python scripts/generate_logs.py
```

4. If you run into Python module errors, ensure the virtualenv is activated and packages from `requirements.txt` are installed.
