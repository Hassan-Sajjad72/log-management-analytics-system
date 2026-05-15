# Log Management and Analytics System

## Short Description

An ADBMS project for collecting, storing, and analyzing structured application logs in PostgreSQL.

## Problem It Solves

The project addresses the difficulty of managing high-volume logs that grow quickly, repeat metadata, and become slow to query when stored without a database design optimized for filtering, aggregation, and time-based analysis.

## Features

- Normalized schema for logs and reference tables
- Synthetic log generation for large-scale testing
- Seed data for reference entities
- Benchmark queries and results for performance comparison
- Documentation for database design, setup, and advanced techniques

## Tech Stack

- PostgreSQL
- Python
- Faker
- psycopg2
- pgAdmin
- VS Code

## Folder Structure

- `scripts/` - log generation script
- `sql/schema/` - table definitions and master schema file
- `sql/seed/` - seed data for reference tables
- `sql/benchmarks/` - benchmark SQL and results
- `docs/` - project documentation and diagrams

## Setup Guide

See [docs/setup_guide.md](docs/setup_guide.md)

## Database Design

See [docs/database_design.md](docs/database_design.md)

## Advanced DB Techniques

See [docs/advanced_db_techniques.md](docs/advanced_db_techniques.md)

## Current Status

The schema, seed files, generator script, benchmark queries, and supporting documentation are in place. The project is ready for database setup, log generation, and query benchmarking.