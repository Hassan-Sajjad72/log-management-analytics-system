# Indexing

## Overview

Indexes were added to speed up the most common `logs` queries in this project, especially time-based filters, service-specific lookups, and error analysis. Instead of scanning the full `logs` table every time, PostgreSQL can use smaller access paths that match the query conditions.

This technique is a good fit for the project because the workload mixes large log ingestion with repeated dashboard and reporting queries.

## What Was Implemented

Five indexes were created for the `logs` table:

1. `idx_log_created_at`
	- single-column index on `created_at DESC`
	- speeds up recent-log queries and time-range filtering

2. `idx_log_log_level_id`
	- single-column index on `log_level_id`
	- speeds up severity-based filtering

3. `idx_log_service_created_at`
	- composite index on `(service_id, created_at DESC)`
	- speeds up service dashboards and recent activity lookups

4. `idx_log_service_log_level`
	- composite index on `(service_id, log_level_id)`
	- speeds up service-specific error analysis

5. `idx_log_errors_only`
	- partial index on `(service_id, created_at DESC)` for `log_level_id IN (4, 5)`
	- keeps the index smaller by targeting only ERROR and CRITICAL rows

These were added in:

- [sql/schema/04_create_indexes.sql](../../sql/schema/04_create_indexes.sql)

Benchmark queries for indexing were added in:

- [sql/benchmarks/indexing/01_before_index_recent_logs.sql](../../sql/benchmarks/indexing/01_before_index_recent_logs.sql)
- [sql/benchmarks/indexing/02_after_index_recent_logs.sql](../../sql/benchmarks/indexing/02_after_index_recent_logs.sql)
- [sql/benchmarks/indexing/03_composite_index_service_errors.sql](../../sql/benchmarks/indexing/03_composite_index_service_errors.sql)
- [sql/benchmarks/indexing/04_partial_index_errors.sql](../../sql/benchmarks/indexing/04_partial_index_errors.sql)

## How It Works

The raw `logs` table stores detailed event-level records. Without indexes, PostgreSQL has to inspect many rows, sort the results, and filter them after reading large parts of the table.

Indexes help by letting PostgreSQL jump directly to the relevant rows:

- `created_at DESC` supports ordered recent-log queries.
- `(service_id, created_at DESC)` helps when a query filters by service and sorts by time.
- `(service_id, log_level_id)` helps when a query filters by service and severity together.
- the partial index only covers ERROR and CRITICAL rows, so it is smaller and cheaper to scan for error-focused queries.

Because these access paths align with the query predicates, PostgreSQL can avoid broad sequential scans and reduce sorting work.

## Example (create index + test query)

Create a descending time index for recent-log queries:

```sql
CREATE INDEX idx_log_created_at ON logs (created_at DESC);
```

Test with an example query and `EXPLAIN ANALYZE` to confirm the index is used:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM logs
WHERE created_at >= now() - interval '1 day'
ORDER BY created_at DESC
LIMIT 100;
```

Compare `EXPLAIN ANALYZE` output before and after creating the index and review whether the plan uses an "Index Scan" or "Index Only Scan".

## Performance Improvement

The biggest gain came from the recent-log query that filters by date and sorts by newest records first. With the index in place, PostgreSQL can satisfy that query much more efficiently than scanning the whole table.

Current benchmark results from the project summary show:

- recent logs query: about 890.627 ms before indexing and 1.635 ms after indexing
- composite service/error query: 0.544 ms after indexing
- partial error query: 221.92 ms after indexing

The strongest improvement is for the recent-log query, where the index reduced response time by roughly 545x.

## Performance Impact

| Query | Benchmark File | Before Indexing | After Indexing | Impact |
| --- | --- | --- | --- | --- |
| Recent logs | [01_before_index_recent_logs.sql](../../sql/benchmarks/indexing/01_before_index_recent_logs.sql) / [02_after_index_recent_logs.sql](../../sql/benchmarks/indexing/02_after_index_recent_logs.sql) | 890.627 ms | 1.635 ms | about 545x faster |
| Service + log level errors | [03_composite_index_service_errors.sql](../../sql/benchmarks/indexing/03_composite_index_service_errors.sql) | not separately measured in the summary | 0.544 ms | very fast index-backed lookup |
| Error-focused service query | [04_partial_index_errors.sql](../../sql/benchmarks/indexing/04_partial_index_errors.sql) | not separately measured in the summary | 221.92 ms | selective partial-index scan |

## Why Performance Improved

Performance improved because:

- the queries now match index keys closely
- ordered scans can use the descending time index instead of sorting large result sets
- composite indexes reduce the number of rows PostgreSQL must check for multi-column filters
- the partial index is smaller than a full-table index, so error lookups touch less data
- index-backed access reduces the need for sequential scans over the full `logs` table

In short, PostgreSQL can use the indexes to narrow down the candidate rows before doing the expensive parts of the query.

## Benefits

- much faster recent-log queries
- better dashboard response times
- faster service-level error analysis
- smaller index footprint for selective error workloads
- improved query plans for common filter patterns

## Trade-Offs

- indexes make inserts and bulk loads slower because PostgreSQL must update the index structures
- indexes use extra storage
- too many indexes can add write overhead without helping real workloads
- partial indexes only help when the query matches the indexed condition

For this project, the read-performance gain is worth the extra write cost because the workload is analytics-heavy.

## Best Use In This Project

Indexes are best for:

- recent activity feeds
- time-based log browsing
- service-specific dashboards
- error and severity analysis
- ordered reporting queries on `logs`

They are not the best choice for:

- write-heavy ingestion paths where insert speed matters more than query speed
- queries that do not filter or sort on indexed columns
- ad hoc filters that do not match the index layout

## Conclusion

Indexes were added as a targeted performance layer for the `logs` table. They significantly reduced query time for the most common lookup patterns by giving PostgreSQL efficient access paths for recent logs, service filters, severity checks, and selective error reporting.

For this project, indexing is a strong fit because the database serves repeated analytics queries over a large log dataset, and those queries benefit directly from well-chosen single-column, composite, and partial indexes.
