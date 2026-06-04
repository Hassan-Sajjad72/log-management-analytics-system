# Log Management and Analytics System

## Short Description

An ADBMS project for collecting, storing, and analyzing structured application logs in PostgreSQL.

## Problem It Solves

The project addresses the difficulty of managing high-volume logs that grow quickly, repeat metadata, and become slow to query when stored without a database design optimized for filtering, aggregation, and time-based analysis.

## Features

- Normalized schema for logs and reference tables
- Synthetic log generation for large-scale testing
- Live log ingestion simulation for dashboard demos
- Seed data for reference entities
- Benchmark queries and results for performance comparison
- Documentation for database design, setup, and advanced techniques
- **Advanced Database Techniques**:
  - Indexing (single-column, composite, partial indexes)
  - Partitioning (range partitioning by date, partition pruning)
  - Materialized Views (precomputed aggregations for dashboards)
  - OLAP aggregation (multi-level summaries)
  - Concurrency Control (MVCC, isolation levels, row-level locking)
  - Query Optimization (optimized queries with better execution plans)

## Tech Stack

- PostgreSQL
- Python
- Faker
- psycopg2
- pgAdmin
- VS Code

## Requirements

- Python 3.10+ (3.11 recommended)
- PostgreSQL 13+
- Recommended: pgAdmin for GUI management

## Quick Start (minimum steps)

1. Create a PostgreSQL database and a database user (see `docs/setup_guide.md`).
2. Apply the base schema and seed reference data (psql or pgAdmin).
3. Start the backend and open the dashboard:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate    # PowerShell/Windows
pip install -r requirements.txt
python app.py
```

4. (Optional) In a second terminal, run the log generator to populate demo data:

```bash
python scripts/generate_logs.py
```

See `docs/setup_guide.md` for full cross-platform commands and environment setup.
## Folder Structure

- `scripts/` - log generation script
  - `generate_logs.py` - bulk synthetic log generation
  - `simulate_live_logs.py` - continuous live log ingestion simulator
- `sql/schema/` - table definitions and master schema file
  - `04_create_indexes.sql` - index creation for optimization
  - `05_create_partitioned_logs.sql` - partitioned table setup
  - `01_create_materialized_views.sql` - materialized view creation
  - `02_refresh_materialized_views.sql` - MV refresh with CONCURRENTLY
  - `03_create_olap_aggregation.sql` - OLAP summary tables
- `sql/seed/` - seed data for reference tables
- `sql/benchmarks/` - benchmark SQL and results
  - `baseline/` - baseline queries without optimization
  - `indexing/` - before/after index performance benchmarks
  - `partitioning/` - partition pruning and comparison benchmarks
  - `materialized_views/` - MV query benchmarks
  - `olap/` - OLAP aggregation query benchmarks
  - `optimized/` - optimized query versions with better plans
  - `concurrency/` - lock monitoring and contention analysis
  - `benchmark_summary.md` - summary of all benchmark results
- `sql/concurrency/` - concurrency control demos
  - `01_isolation_levels_demo.sql` - READ COMMITTED vs REPEATABLE READ
  - `02_row_level_locking_demo.sql` - SELECT FOR UPDATE examples
  - `03_concurrent_insert_simulation.sql` - concurrent inserts
  - `04_deadlock_prevention_demo.sql` - lock ordering strategies
  - `05_mvcc_visibility_demo.sql` - MVCC and VACUUM demonstration
- `docs/` - project documentation and diagrams
  - `techniques/` - advanced technique documentation
    - `materialized_views.md` - MV explanation and impact
    - `indexing.md` - index strategies and performance
    - `partitioning.md` - range partitioning and pruning
    - `concurrency_control.md` - MVCC and isolation levels
    - `query_optimization.md` - optimization techniques
    - `olap_aggregation.md` - OLAP design patterns

## Setup Guide

See [docs/setup_guide.md](docs/setup_guide.md)

## Database Design

See [docs/database_design.md](docs/database_design.md)

## Advanced DB Techniques

See [docs/advanced_db_techniques.md](docs/advanced_db_techniques.md)

## Backend Dashboard

The project includes a Flask backend dashboard for viewing logs and analytics.

### Pages

- `/` - Dashboard overview
- `/logs` - Filter and view logs
- `/analytics` - Materialized view analytics
- `/analytics/olap` - OLAP aggregation dashboard
- `/techniques` - Advanced DB technique usage
- `/benchmarks` - Benchmark results

### APIs

- `/api/health`
- `/api/logs`
- `/api/logs/<int:log_id>`
- `/api/services`
- `/api/analytics/summary`
- `/api/analytics/errors-by-service`
- `/api/analytics/endpoint-latency`
- `/api/analytics/daily-service-activity`
- `/api/analytics/daily-endpoint-latency`
- `/api/analytics/status-code-distribution`
- `/api/analytics/olap/daily-totals`
- `/api/analytics/olap/service-summary`
- `/api/analytics/olap/endpoint-summary`

## How to Run Backend

```bash
cd backend
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## How to Simulate Live Logs

Run this in a separate terminal from the project root while the backend dashboard is open:

```bash
python scripts/simulate_live_logs.py
```

Optional environment variables:

- `LIVE_BATCH_SIZE` - logs inserted per batch, default `50`
- `LIVE_INTERVAL_SECONDS` - delay between batches, default `2`
- `LIVE_MAX_BATCHES` - stop after this many batches, default `0` for continuous mode

Notes:
- There are two example env files: `.env.example` in the repository root (used by CLI generators and scripts) and `backend/.env.example` (used by the Flask backend). Copy the relevant file to `.env` or `backend/.env` and populate values before running the backend or generators.
- Use `PGPASSWORD` or a `.pgpass` file to avoid being prompted for the DB password when running `psql` commands.
## Current Status

The project is in final demo/prototype phase. The PostgreSQL schema, seed data, synthetic log generator, advanced database techniques, benchmark queries, Flask dashboard, JSON APIs, screenshots, and supporting documentation are in place.
