# Project Overview

## What the system does

This is a Log Management & Analytics System that collects, stores, and analyzes application and infrastructure logs. It centralizes logs from services and servers, enriches them with metadata (service, server, user, endpoint, log level, error category, status code, IP address, response time, timestamp), and provides a foundation for querying, reporting, and benchmarking performance and reliability metrics.

## Why this project exists

- To provide a realistic dataset and tooling for studying log ingestion, storage, and query performance on PostgreSQL.
- To enable students and engineers to prototype analytics queries, test indexing and partitioning strategies, and evaluate optimization techniques for large time-series-style log datasets.

## Objectives

- Create a normalized schema for structured logs and related dimensions (services, servers, users, endpoints, error categories, log levels).
- Provide scripts to seed reference tables and generate large volumes of synthetic logs for benchmarking.
- Measure baseline query performance and record observations to guide schema/indexing improvements.
