# Partitioning

## Overview

Range partitioning was added to split the `logs` table by `created_at` time ranges. This fits log data well because logs are naturally time-series data, data growth is predictable over time, and most analytics queries filter by recent days or months.

Instead of searching one very large table for every query, PostgreSQL can target only the relevant monthly partitions. This reduces scanned data and keeps query latency more stable as total log volume grows.

## What Was Implemented

The `logs` table was converted from a flat table to a range-partitioned table:

1. Original table renamed to `logs_unpartitioned` (backup for comparison)
2. New parent `logs` table created with `PARTITION BY RANGE (created_at)`
3. Monthly partitions created
4. Default partition added for out-of-range rows
5. Existing rows migrated into the partitioned table

Important schema detail:

- Primary key changed from a single column to a composite key: `(log_id, created_at)`
- This is required because PostgreSQL needs the partition key to be part of unique constraints on a partitioned table.

This was added in:

- [sql/schema/05_create_partitioned_logs.sql](../../sql/schema/05_create_partitioned_logs.sql)

Benchmark queries for partitioning were added in:

- [sql/benchmarks/partitioning/01_partition_pruning_check.sql](../../sql/benchmarks/partitioning/01_partition_pruning_check.sql)
- [sql/benchmarks/partitioning/02_cross_partition_query.sql](../../sql/benchmarks/partitioning/02_cross_partition_query.sql)
- [sql/benchmarks/partitioning/03_single_partition_error_query.sql](../../sql/benchmarks/partitioning/03_single_partition_error_query.sql)
- [sql/benchmarks/partitioning/04_flat_vs_partitioned_comparison.sql](../../sql/benchmarks/partitioning/04_flat_vs_partitioned_comparison.sql)

## How It Works

With range partitioning, each row is stored in a child table based on `created_at`. For example, one month of logs goes to one partition, next month goes to another.

When a query has a time filter, PostgreSQL can apply partition pruning. Partition pruning means the planner skips partitions that cannot contain matching rows.

Example:

- Query filter: `created_at >= '2026-04-01' AND created_at < '2026-05-01'`
- Expected behavior: only the partition covering April 2026 is scanned (or very few partitions), not all monthly partitions.

How to confirm in `EXPLAIN` output:

- Look for a partition-pruning indicator such as `Partitions: 1 of 4` (or similar count).
- Fewer scanned partitions usually means less I/O and faster execution.

Use [sql/benchmarks/partitioning/01_partition_pruning_check.sql](../../sql/benchmarks/partitioning/01_partition_pruning_check.sql) to verify pruning behavior.

## Performance Improvement

The largest gains are typically seen in queries that are tightly scoped to a single month (or short time range), because pruning avoids scanning irrelevant partitions.

In this project, partitioning targets:

- month-scoped service and error analysis
- recent-window aggregations (for example last 30 to 60 days)
- comparisons between partitioned `logs` and flat `logs_unpartitioned`

## Performance Impact

Run the benchmark queries and record `Execution Time` from `EXPLAIN (ANALYZE, BUFFERS)`.

| Query | Benchmark File | Before (Flat Table) | After (Partitioned) | Impact |
| --- | --- | --- | --- | --- |
| Single-month service counts | [04_flat_vs_partitioned_comparison.sql](../../sql/benchmarks/partitioning/04_flat_vs_partitioned_comparison.sql) vs [01_partition_pruning_check.sql](../../sql/benchmarks/partitioning/01_partition_pruning_check.sql) | _fill from `logs_unpartitioned` run_ | _fill from `logs` run_ | expected faster when pruning is effective |
| Cross-partition 60-day aggregation | [04_flat_vs_partitioned_comparison.sql](../../sql/benchmarks/partitioning/04_flat_vs_partitioned_comparison.sql) vs [02_cross_partition_query.sql](../../sql/benchmarks/partitioning/02_cross_partition_query.sql) | _fill from flat-table equivalent_ | _fill from partitioned run_ | depends on partition count and aggregation cost |
| Single-month error analysis | [04_flat_vs_partitioned_comparison.sql](../../sql/benchmarks/partitioning/04_flat_vs_partitioned_comparison.sql) vs [03_single_partition_error_query.sql](../../sql/benchmarks/partitioning/03_single_partition_error_query.sql) | _fill from flat-table equivalent_ | _fill from partitioned run_ | usually improved by pruning + smaller scan scope |

## Why Performance Improved

Performance improves mainly because:

- partition pruning excludes irrelevant partitions before execution
- each partition is smaller than the full table, reducing scanned blocks
- cache locality is better for recent, frequently queried partitions
- maintenance operations can be more targeted (for example, partition-level actions)

For time-filtered analytics, this often gives more predictable query times as data volume grows.

## Benefits

- faster time-range queries when pruning applies
- better scalability for continuously growing log data
- easier data lifecycle management (archive/drop old partitions)
- cleaner operational control by month/time window

## Trade-Offs

- partition management overhead: new partitions must be created and maintained over time
- query design must include partition key filters (`created_at`) to benefit fully
- primary key/unique constraint design changes are required (for example `(log_id, created_at)`)
- migration from a flat table adds operational complexity
- too many tiny partitions can hurt planning performance

## Best Use In This Project

Partitioning is best for:

- time-window analytics dashboards
- monthly service and error reports
- high-volume log retention with predictable growth
- workloads where old data is archived/dropped by date

Partitioning is less useful for:

- queries without time filters
- small datasets where a single table is already fast
- workloads dominated by random key lookups unrelated to `created_at`

## Conclusion

Range partitioning was implemented to align the physical layout of `logs` with the time-series nature of the data. It enables partition pruning, which can significantly reduce scanned data for month-scoped and recent-window queries.

For this project, partitioning is a strong long-term strategy because log volume grows predictably over time and most analytical queries are naturally filtered by date.
