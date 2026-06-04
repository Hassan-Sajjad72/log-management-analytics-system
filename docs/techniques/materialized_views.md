# Materialized Views

## Overview

Materialized views were added to speed up repeated analytics queries on the `logs` table. Instead of scanning and aggregating more than 1 million log rows every time, PostgreSQL stores precomputed summary results and serves analytics from those summaries.

This technique is especially useful for dashboard and reporting queries that repeat the same aggregations again and again.

## What Was Implemented

Three materialized views were created:

1. `mv_daily_service_activity`
   - daily log count per service
   - daily error count per service
   - average response time per service

2. `mv_daily_endpoint_latency`
   - daily request count per endpoint
   - average response time per endpoint
   - maximum response time per endpoint

3. `mv_daily_status_code_distribution`
   - daily count of each HTTP status code

These were added in:

- [sql/schema/01_create_materialized_views.sql](/D:/Academia/Semester%206/Advanced%20DBMS/Project/log-management-analytics-system/sql/schema/01_create_materialized_views.sql)
- [sql/schema/02_refresh_materialized_views.sql](/D:/Academia/Semester%206/Advanced%20DBMS/Project/log-management-analytics-system/sql/schema/02_refresh_materialized_views.sql)

- [sql/schema/01_create_materialized_views.sql](../../sql/schema/01_create_materialized_views.sql)
- [sql/schema/02_refresh_materialized_views.sql](../../sql/schema/02_refresh_materialized_views.sql)

Benchmark queries for the materialized views were added in:

- [sql/benchmarks/materialized_views/01_service_activity_from_mv.sql](/D:/Academia/Semester%206/Advanced%20DBMS/Project/log-management-analytics-system/sql/benchmarks/materialized_views/01_service_activity_from_mv.sql)
- [sql/benchmarks/materialized_views/02_slowest_endpoints_from_mv.sql](/D:/Academia/Semester%206/Advanced%20DBMS/Project/log-management-analytics-system/sql/benchmarks/materialized_views/02_slowest_endpoints_from_mv.sql)
- [sql/benchmarks/materialized_views/03_status_code_distribution_from_mv.sql](/D:/Academia/Semester%206/Advanced%20DBMS/Project/log-management-analytics-system/sql/benchmarks/materialized_views/03_status_code_distribution_from_mv.sql)

## How It Works

The raw `logs` table stores detailed event-level records. Analytics queries such as service activity, slow endpoints, and status code distribution normally have to:

- scan a large number of rows
- group the rows
- calculate counts and averages
- sort the results

Materialized views store these grouped results in advance. When the analytics query runs, PostgreSQL reads the much smaller summarized dataset instead of recalculating everything from the raw table.

After new logs are inserted, the views are updated using:

```bash
# Refresh all materialized views (example):
psql -h localhost -U log_user -d log_management -f sql/schema/02_refresh_materialized_views.sql
```

## Example (create + refresh)

Create an example materialized view for daily service activity:

```sql
CREATE MATERIALIZED VIEW mv_daily_service_activity AS
SELECT date_trunc('day', created_at) AS day,
       service_id,
       COUNT(*) AS total_requests,
       SUM(CASE WHEN log_level_id IN (4,5) THEN 1 ELSE 0 END) AS error_count,
       AVG(response_time_ms) AS avg_response_time
FROM logs
GROUP BY 1, service_id;
```

To refresh (concurrently when supported):

```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_service_activity;
```

Note: `CONCURRENTLY` requires a unique index on the materialized view and is not supported inside a transaction block.

## Performance Improvement

The improvement came from reducing the amount of data scanned at query time.

Current summary sizes:

- `mv_daily_service_activity`: 910 rows
- `mv_daily_endpoint_latency`: 4550 rows
- `mv_daily_status_code_distribution`: 27391 rows

Current raw table size:

- `logs`: 1000100 rows

Measured benchmark results on the current dataset:

| Query | Raw Table Time | Materialized View Time | Improvement |
| --- | --- | --- | --- |
| Service activity | 242.17 ms | 0.63 ms | about 386x faster |
| Slowest endpoints | 254.35 ms | 1.80 ms | about 141x faster |
| Status code distribution | 245.88 ms | 7.33 ms | about 34x faster |

## Why Performance Improved

Performance improved because:

- repeated `GROUP BY` operations were precomputed
- averages and counts were already summarized
- much fewer rows had to be scanned
- day-based filtering worked on compact summary data
- the views also have indexes to support refresh and filtering

In the raw-table version, PostgreSQL performed parallel sequential scans over the `logs` table. In the materialized-view version, PostgreSQL read a much smaller pre-aggregated result set.

## Benefits

- much faster analytics queries
- better support for dashboards and reports
- reduced repeated CPU work
- simpler reporting SQL because major aggregations are already prepared

## Trade-Offs

- materialized views are not real-time
- they need manual or scheduled refresh after new data is inserted
- they use extra storage
- refresh operations also consume time and system resources

This means materialized views improve read performance, but freshness depends on how often they are refreshed.

## Best Use In This Project

Materialized views are best for:

- dashboard summaries
- daily service performance reports
- endpoint latency analysis
- status code trend analysis

They are not the best choice for:

- real-time live monitoring
- queries that need every latest inserted row immediately

## Conclusion

Materialized views were implemented as a summary layer above the `logs` table. They significantly reduced query execution time for repeated analytics workloads by storing precomputed daily aggregates.

For this project, they are a strong fit because the workload is analytics-heavy and the same summary queries are likely to be used repeatedly in reports and dashboards.
