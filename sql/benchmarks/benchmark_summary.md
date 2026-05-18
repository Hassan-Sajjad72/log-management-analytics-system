# Benchmark Summary: Advanced Database Techniques

## Executive Summary

This document consolidates performance benchmarks for all advanced database optimization techniques applied to the log-management system. Each technique demonstrates significant speedups for specific query patterns.

**Dataset**: 1,000,000+ log records across multiple services over 90-day window

## Consolidated Performance Comparison

| Technique | Query Pattern | Execution Time (Before) | Execution Time (After) | Speedup | Key Benefit |
| --- | --- | --- | --- | --- | --- |
| **Materialized Views** | Service activity (30-day aggregation) | 242+ ms | 0.363 ms | ~668x | Precomputed daily summaries |
| **Materialized Views** | Slowest endpoints (30-day) | 254+ ms | 0.877 ms | ~290x | Aggregation caching |
| **Materialized Views** | Status code distribution (30-day) | 246+ ms | 6.924 ms | ~36x | Summary data reduction |
| **OLAP** | Service error trend (daily-service level) | Dashboard latency | 1.423 ms | baseline | Multi-level aggregation |
| **OLAP** | Log level trend (daily-level) | Dashboard latency | 1.733 ms | baseline | Flexible rollup queries |
| **OLAP** | Daily total metrics | Dashboard latency | 0.829 ms | baseline | Fast top-level summary |
| **Indexing** | Recent logs (7-day with sort) | 890.627 ms | 1.635 ms | ~545x | Time-based filtering + ordering |
| **Indexing** | Service + log level composite | Index coverage | 0.544 ms | baseline | Multi-column filtering |
| **Indexing** | Partial index (errors only) | Full table scan | 221.92 ms | selective | Selective error analysis |
| **Partitioning** | Single-month date range | ~500+ ms | 486.017 ms | partition pruning | Month-scoped queries |
| **Partitioning** | Cross-partition (60-day aggregation) | ~600+ ms | 1394.995 ms | overhead | Multi-partition scans |
| **Partitioning** | Single-partition error query | ~200+ ms | 77.615 ms | ~2.5x | Pruning on tight filter |
| **Partitioning** | Flat vs Partitioned (2-month window) | 166.971 ms | 166.971 ms | ~1x | Partition alignment effect |

---

## 1. Materialized Views

Materialized views precompute and cache aggregations, eliminating the need to scan raw logs repeatedly.

### Key Metrics

| Query | Benchmark File | Execution Time | Use Case |
| --- | --- | --- | --- |
| Service Activity (30-day) | [materialized_views/01_service_activity_from_mv.sql](materialized_views/01_service_activity_from_mv.sql) | 0.363 ms | Dashboard: service metrics by day |
| Slowest Endpoints (30-day) | [materialized_views/02_slowest_endpoints_from_mv.sql](materialized_views/02_slowest_endpoints_from_mv.sql) | 0.877 ms | Dashboard: endpoint latency trends |
| Status Code Distribution (30-day) | [materialized_views/03_status_code_distribution_from_mv.sql](materialized_views/03_status_code_distribution_from_mv.sql) | 6.924 ms | Dashboard: response status summary |

### Schema

- [sql/schema/01_create_materialized_views.sql](../schema/01_create_materialized_views.sql)
- [sql/schema/02_refresh_materialized_views.sql](../schema/02_refresh_materialized_views.sql) — uses CONCURRENTLY for non-blocking refresh

### Benefits
- Extreme speedup for repeated aggregations (>100x typical)
- Non-blocking refresh with CONCURRENTLY
- Real-time availability after refresh

### Trade-Offs
- Not real-time; freshness depends on refresh frequency
- Extra storage for summary tables
- Maintenance overhead for manual/scheduled refresh

---

## 2. OLAP Aggregation

OLAP (Online Analytical Processing) creates multi-level summary tables for dimensional analysis.

### Key Metrics

| Query | Benchmark File | Execution Time | Use Case |
| --- | --- | --- | --- |
| Service Error Trend (day-service level) | [olap/01_service_error_trend_from_olap.sql](olap/01_service_error_trend_from_olap.sql) | 1.423 ms | Trend: errors by service over time |
| Log Level Trend (day-level) | [olap/02_log_level_trend_from_olap.sql](olap/02_log_level_trend_from_olap.sql) | 1.733 ms | Trend: severity distribution by day |
| Daily Total Metrics | [olap/03_daily_totals_from_olap.sql](olap/03_daily_totals_from_olap.sql) | 0.829 ms | Summary: total requests, errors, latency |

### Schema

- [sql/schema/03_create_olap_aggregation.sql](../schema/03_create_olap_aggregation.sql)

### Benefits
- Fast multi-dimensional queries
- Support for hierarchical rollups (e.g., total → by service → by endpoint)
- Flexible aggregation levels
- Consistent query performance across dimensions

### Trade-Offs
- Requires careful design of aggregation dimensions
- Storage overhead for pre-aggregated data
- Refresh and maintenance complexity

---

## 3. Indexing

Indexes provide fast access paths for filtered and sorted queries without scanning full tables.

### Key Metrics

| Query | Benchmark File | Before Indexing | After Indexing | Speedup |
| --- | --- | --- | --- | --- |
| Recent Logs (7-day, sorted) | [indexing/01_before_index_recent_logs.sql](indexing/01_before_index_recent_logs.sql) / [indexing/02_after_index_recent_logs.sql](indexing/02_after_index_recent_logs.sql) | 890.627 ms | 1.635 ms | ~545x |
| Service + Error Composite | [indexing/03_composite_index_service_errors.sql](indexing/03_composite_index_service_errors.sql) | full scan | 0.544 ms | very fast |
| Partial Index (errors only) | [indexing/04_partial_index_errors.sql](indexing/04_partial_index_errors.sql) | full scan | 221.92 ms | selective |

### Indexes Created

- [sql/schema/04_create_indexes.sql](../schema/04_create_indexes.sql)
  - `idx_log_created_at` (DESC) — time-range filtering
  - `idx_log_log_level_id` — severity filtering
  - `idx_log_service_created_at` (composite) — service + time
  - `idx_log_service_log_level` (composite) — service + severity
  - `idx_log_errors_only` (partial) — ERROR/CRITICAL rows only

### Benefits
- Dramatic speedup for time and key-based filters
- Multi-column indexes align with common query patterns
- Partial indexes keep overhead low for selective workloads

### Trade-Offs
- Slower inserts/updates (index maintenance)
- Extra storage for index structures
- Query planner must choose appropriate index

---

## 4. Partitioning

Range partitioning divides the logs table by date, enabling partition pruning for time-filtered queries.

### Key Metrics

| Query | Benchmark File | Execution Time | Notes |
| --- | --- | --- | --- |
| Single-month pruning (Apr-May 2026) | [partitioning/01_partition_pruning_check.sql](partitioning/01_partition_pruning_check.sql) | 486.017 ms | 1-2 partitions scanned |
| Cross-partition (60-day aggregation) | [partitioning/02_cross_partition_query.sql](partitioning/02_cross_partition_query.sql) | 1394.995 ms | ~2-3 partitions scanned |
| Single-partition error query | [partitioning/03_single_partition_error_query.sql](partitioning/03_single_partition_error_query.sql) | 77.615 ms | Single partition + error filter |
| Flat vs Partitioned (2-month) | [partitioning/04_flat_vs_partitioned_comparison.sql](partitioning/04_flat_vs_partitioned_comparison.sql) | 166.971 ms | Comparable performance at scale |

### Schema

- [sql/schema/05_create_partitioned_logs.sql](../schema/05_create_partitioned_logs.sql)
  - Monthly range partitions
  - Primary key: `(log_id, created_at)` — partition key required in PK
  - Default partition for out-of-range rows

### Benefits
- Partition pruning eliminates irrelevant partitions
- Better scalability for growing datasets
- Easier lifecycle management (archive/drop old partitions)
- Predictable latency as table grows

### Trade-Offs
- Partition management overhead (creating new partitions monthly)
- PK schema change required
- Cross-partition queries still scan multiple partitions
- Query must include date filters to benefit fully

---

## 5. Query Optimization

Optimized queries rewrite logic to improve execution plans without schema changes.

### Benchmarked Optimizations

Optimized query versions are located in [optimized/](optimized/):

- [optimized/01_recent_logs_optimized.sql](optimized/01_recent_logs_optimized.sql)
- [optimized/02_errors_by_service_optimized.sql](optimized/02_errors_by_service_optimized.sql)
- [optimized/03_slowest_endpoints_optimized.sql](optimized/03_slowest_endpoints_optimized.sql)
- [optimized/04_status_code_distribution_optimized.sql](optimized/04_status_code_distribution_optimized.sql)
- [optimized/05_service_activity_optimized.sql](optimized/05_service_activity_optimized.sql)

See [optimized/optimized_results.md](optimized/optimized_results.md) for detailed query plan improvements.

---

## 6. Baseline Queries

Original unoptimized queries are in [baseline/](baseline/) for reference:

- [baseline/01_recent_logs.sql](baseline/01_recent_logs.sql)
- [baseline/02_errors_by_service.sql](baseline/02_errors_by_service.sql)
- [baseline/03_slowest_endpoints.sql](baseline/03_slowest_endpoints.sql)
- [baseline/04_status_code_distribution.sql](baseline/04_status_code_distribution.sql)
- [baseline/05_service_activity.sql](baseline/05_service_activity.sql)

See [baseline/baseline_results.md](baseline/baseline_results.md) for baseline timing and execution plans.

---

## Key Insights

1. **Materialized Views** deliver the best speedup for precomputed aggregations (>100x for repeated queries).
2. **Indexing** is essential for raw table queries, especially time-based filters (545x improvement on 7-day recent logs).
3. **Partitioning** helps with single-partition queries but adds overhead for cross-partition scans.
4. **OLAP** provides consistent performance for dimensional analysis without the cache-invalidation concerns of MVs.
5. **Combined approach** is most effective: MVs for dashboards, indexes for raw queries, partitioning for scalability.

## Recommendations

- **For dashboards**: Use materialized views or OLAP with CONCURRENTLY refresh.
- **For ad hoc queries on raw logs**: Ensure indexes match filter/sort patterns.
- **For scalability and lifecycle management**: Implement partitioning by date.
- **For consistent performance**: Monitor and refresh materialized views regularly.
- **For real-time requirements**: Accept no-cache approach or accept eventual consistency with bounded staleness.