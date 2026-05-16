# Query Optimization

## Overview

Query optimization was implemented to improve analytics performance without changing the logical database schema. The goal was to reduce unnecessary work at query time by writing leaner SQL and by routing repeated analytical workloads to pre-aggregated materialized views.

In this project, query optimization was applied in two ways:

- rewriting raw-table queries to be more selective
- replacing expensive repeated aggregations with summary-backed queries

## What Was Implemented

A separate optimized benchmark set was created in:

- [sql/benchmarks/optimized/01_recent_logs_optimized.sql](/D:/Academia/Semester%206/Advanced%20DBMS/Project/log-management-analytics-system/sql/benchmarks/optimized/01_recent_logs_optimized.sql)
- [sql/benchmarks/optimized/02_errors_by_service_optimized.sql](/D:/Academia/Semester%206/Advanced%20DBMS/Project/log-management-analytics-system/sql/benchmarks/optimized/02_errors_by_service_optimized.sql)
- [sql/benchmarks/optimized/03_slowest_endpoints_optimized.sql](/D:/Academia/Semester%206/Advanced%20DBMS/Project/log-management-analytics-system/sql/benchmarks/optimized/03_slowest_endpoints_optimized.sql)
- [sql/benchmarks/optimized/04_status_code_distribution_optimized.sql](/D:/Academia/Semester%206/Advanced%20DBMS/Project/log-management-analytics-system/sql/benchmarks/optimized/04_status_code_distribution_optimized.sql)
- [sql/benchmarks/optimized/05_service_activity_optimized.sql](/D:/Academia/Semester%206/Advanced%20DBMS/Project/log-management-analytics-system/sql/benchmarks/optimized/05_service_activity_optimized.sql)

The optimization strategy was:

1. avoid `SELECT *` where all columns are not needed
2. reduce row width for raw browsing queries
3. remove repeated heavy aggregations from the `logs` table
4. use materialized views for dashboard-style analytical queries
5. compare all optimized queries using `EXPLAIN ANALYZE BUFFERS`

## Research-Backed Techniques That Can Be Used Here

Based on PostgreSQL query-planning and optimization features, these techniques are suitable for this project:

### Techniques Already Used In This Project

- `EXPLAIN (ANALYZE, BUFFERS)`
  Used to compare baseline and optimized query plans, execution time, scan behavior, and buffer usage.

- `Query rewriting`
  Used to simplify SQL and reduce unnecessary work, especially by avoiding repeated heavy aggregation on the raw `logs` table.

- `Avoiding SELECT *`
  Used in the recent-logs query to reduce row width and fetch only the columns actually needed.

- `Materialized-view-backed query routing`
  Used for analytics queries such as service activity, slow endpoints, and status code distribution so they read summarized data instead of rescanning the fact table.

- `Parallel query`
  PostgreSQL already used parallel execution in several baseline plans, which shows that the optimizer recognized full-table analytics as parallelizable workloads.

### Techniques That Can Also Be Applied Later

- `Planner statistics maintenance with ANALYZE`
  Important after large log loads so PostgreSQL has accurate row-distribution statistics and can choose better plans.

- `Extended statistics with CREATE STATISTICS`
  Useful when columns are correlated and PostgreSQL might otherwise make poor estimates. In this project, likely candidates include `service_id` with `log_level_id`, and possibly `service_id` with `endpoint_id`.

- `B-tree and multicolumn index support for optimized queries`
  Especially useful for time-filtered and ordered queries such as recent logs, or service-based filtering with time windows.

- `Index-only scans and covering indexes`
  Potentially useful for raw browsing queries if the needed columns are fully covered by the index and visibility checks can often be skipped.

- `Partition pruning`
  Very useful for time-range queries once the `logs` table is partitioned by `created_at`, because PostgreSQL can avoid scanning irrelevant partitions.

### Techniques That Are Possible But Less Ideal Right Now

- `Partial indexes`
  These can be powerful, but they only help when the predicate is selective and closely matches actual query filters.

- `BRIN indexes`
  These are best when physical row order strongly correlates with the filtered column. They may become more useful if future ingestion is strictly append-by-time.

## Query-By-Query Changes

### 1. Recent Logs

The baseline query used:

```sql
SELECT *
FROM logs
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC
LIMIT 100;
```

The optimized version selects only needed columns:

```sql
SELECT
    log_id,
    request_id,
    service_id,
    endpoint_id,
    status_code,
    response_time_ms,
    created_at
FROM logs
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY created_at DESC
LIMIT 100;
```

This reduces row width and avoids pulling unnecessary data.

### 2. Errors By Service

The baseline query counted errors directly from the raw `logs` table using a scalar subquery on `log_levels`.

The optimized version reads from `mv_daily_service_activity` and sums precomputed `error_logs`. This avoids rescanning the full fact table and redoing the grouping work.

### 3. Slowest Endpoints

The baseline query calculated average response time directly from all log rows.

The optimized version reads from `mv_daily_endpoint_latency` and computes the final ranking from daily endpoint summaries instead of the raw table.

### 4. Status Code Distribution

The baseline query grouped all log rows by `status_code`.

The optimized version reads from `mv_daily_status_code_distribution` and sums already-grouped daily counts.

### 5. Service Activity

The baseline query counted recent service activity directly from the `logs` table.

The optimized version reads from `mv_daily_service_activity`, filters by day, and aggregates the daily summaries.

## How It Improved Performance

The main improvement came from changing the execution path for analytical queries.

Before optimization, PostgreSQL had to:

- scan a large portion of the `logs` table
- group raw rows
- calculate counts and averages repeatedly
- sort the results for each analytics request

After optimization, PostgreSQL often reads already-aggregated summary rows from materialized views instead of recomputing the analytics from scratch.

This means:

- fewer rows are scanned
- less memory is used for grouping
- less CPU time is spent recalculating repeated metrics
- query execution becomes much faster for report-style workloads

## Performance Impact

Measured results on the current dataset:

| Query | Baseline Time | Optimized Time | Improvement |
| --- | --- | --- | --- |
| Recent logs | 242.98 ms | 194.51 ms | about 1.25x faster |
| Errors by service | 248.89 ms | 0.87 ms | about 287x faster |
| Slowest endpoints | 254.35 ms | 6.63 ms | about 38x faster |
| Status code distribution | 245.88 ms | 14.96 ms | about 16x faster |
| Service activity | 242.17 ms | 1.02 ms | about 237x faster |

One important observation in this project is that raw-query optimization alone gives only limited improvement when the database still scans the large `logs` table. The biggest gains come when query optimization is combined with materialized views.

This is why the optimized analytical queries were routed to the summary layer you already implemented.

For the recent-logs query, the gain was smaller because the query still depends on the raw `logs` table and does not yet benefit from teammate work such as indexing or partitioning. For the analytical queries, the gains were much larger because repeated aggregation work was removed from query time.

## Why This Technique Matters

Query optimization is important because it improves performance without changing user-facing functionality. The result returned by the query stays the same, but the path used to compute it becomes more efficient.

It also prepares the project for future gains from:

- indexing
- partitioning
- OLAP summaries

When those techniques are added later, the optimized query structure can benefit from them immediately.

## Trade-Offs

- optimized SQL can become more specialized for specific workloads
- summary-backed queries depend on materialized-view refresh timing
- there may be two versions of a query in the repo: baseline and optimized
- direct raw-table queries are still needed for comparison and validation

## Conclusion

Query optimization in this project focused on making analytical SQL more efficient and more realistic for dashboard/reporting use. The strongest improvements came from routing repeated aggregation queries away from the large `logs` table and toward precomputed summary data.

This makes query optimization a practical bridge between raw schema design and higher-performance analytics architecture.
