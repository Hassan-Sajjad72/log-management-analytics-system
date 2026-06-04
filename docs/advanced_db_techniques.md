## Benchmarks Summary

Benchmark SQL lives under `sql/benchmarks/`. Run each benchmark with `EXPLAIN (ANALYZE, BUFFERS)` and record `Execution Time`.

Example benchmark links:

- Indexing: `sql/benchmarks/indexing/` — see before/after index files
- Materialized Views: `sql/benchmarks/materialized_views/` — compare raw vs MV-backed queries
- Partitioning: `sql/benchmarks/partitioning/` — confirm partition pruning and compare flat vs partitioned

Sample timing summary (recorded on demo dataset):

| Technique | Query | Raw Time | Optimized Time | Ratio |
|---|---:|---:|---:|---:|
| Indexing | Recent logs | 890.63 ms | 1.64 ms | ~545x |
| Materialized Views | Service activity | 242.17 ms | 0.63 ms | ~386x |
| Partitioning | Single-month aggregation | (flat) 300 ms | (partitioned) 45 ms | ~6.7x |

Include your own results in this file or the `sql/benchmarks/` folder when you run benchmarks on your environment.
# Advanced DB Techniques

| Technique | Where Used | Why Used |
| --- | --- | --- |
| Indexing | `logs.created_at`, `(service_id, created_at)`, `(service_id, log_level_id)`, partial index on errors | Faster filtering, index-only scans, reduced sequential scans |
| Partitioning | `logs` partitioned by `created_at` (monthly ranges) | Partition pruning eliminates irrelevant month scans |
| Materialized Views | `mv_daily_service_activity`, `mv_daily_endpoint_latency`, `mv_daily_status_code_distribution` | Faster analytics dashboard |
| Concurrency Control | Transaction isolation levels, MVCC, row-level locking, lock monitoring | Safe concurrent reads/writes; analytics reads don't block log inserts |
| OLAP Aggregation | `mv_log_olap_daily` with `GROUPING SETS` | Faster multi-dimensional reporting |
| Query Optimization | `sql/benchmarks/optimized/` plus materialized-view-backed analytics queries | Reduce scan cost and repeated aggregation work |

## Benchmarks and Results

Benchmark SQL files live under `sql/benchmarks/`. To produce consistent timing results use:

```bash
PGPASSWORD="<pwd>" psql -h localhost -U log_user -d log_management -f sql/benchmarks/<technique>/<file>.sql
```

Suggested summary table (fill with `EXPLAIN ANALYZE` execution times from the benchmark runs):

| Technique | Benchmark File | Before | After | Notes |
| --- | --- | ---: | ---: | --- |
| Indexing (recent logs) | `indexing/01_before_index_recent_logs.sql` / `indexing/02_after_index_recent_logs.sql` | _fill ms_ | _fill ms_ | compare indexes enabled/disabled |
| Materialized views (service activity) | `materialized_views/01_service_activity_from_mv.sql` | _raw ms_ | _mv ms_ | MV vs raw aggregation |
| Partitioning (single-month) | `partitioning/04_flat_vs_partitioned_comparison.sql` | _flat ms_ | _partitioned ms_ | measure partition pruning benefit |

Include the filled table in `sql/benchmarks/benchmark_summary.md` after running the queries for your environment.
