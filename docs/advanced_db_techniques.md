# Advanced DB Techniques

| Technique | Where Used | Why Used |
| --- | --- | --- |
| Indexing | `logs.created_at`, `service_id`, `log_level_id` | Faster filtering |
| Composite Indexing | `(service_id, created_at)` | Faster service-wise time queries |
| Partitioning | `logs` by `created_at` | Faster recent log queries |
| Materialized Views | `mv_daily_service_activity`, `mv_daily_endpoint_latency`, `mv_daily_status_code_distribution` | Faster analytics dashboard |
| Query Optimization | `sql/benchmarks/optimized/` plus materialized-view-backed analytics queries | Reduce scan cost and repeated aggregation work |
| Full Text Search | `message` column | Search log messages |
| Normalization | reference tables | Avoid repeated metadata |
