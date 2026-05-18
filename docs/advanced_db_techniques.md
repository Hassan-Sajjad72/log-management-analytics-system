# Advanced DB Techniques

| Technique | Where Used | Why Used |
| --- | --- | --- |
| Indexing | `logs.created_at`, `(service_id, created_at)`, `(service_id, log_level_id)`, partial index on errors | Faster filtering, index-only scans, reduced sequential scans |
| Partitioning | `logs` partitioned by `created_at` (monthly ranges) | Partition pruning eliminates irrelevant month scans |
| Materialized Views | `mv_daily_service_activity`, `mv_daily_endpoint_latency`, `mv_daily_status_code_distribution` | Faster analytics dashboard |
| Concurrency Control | Transaction isolation levels, MVCC, row-level locking, lock monitoring | Safe concurrent reads/writes; analytics reads don't block log inserts |
| OLAP Aggregation | `mv_log_olap_daily` with `GROUPING SETS` | Faster multi-dimensional reporting |
| Query Optimization | `sql/benchmarks/optimized/` plus materialized-view-backed analytics queries | Reduce scan cost and repeated aggregation work |
