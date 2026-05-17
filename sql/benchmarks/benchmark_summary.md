# 1. Materialized Views

## Query - 1: `01_service_activtiy_from_mv.sql`
EXPLAIN ANALYZE
SELECT
    service_id,
    service_name,
    SUM(total_logs) AS log_count,
    ROUND(
        SUM(total_response_time_ms)::numeric
        / NULLIF(SUM(total_logs), 0),
        2
    ) AS avg_response_time_ms
FROM mv_daily_service_activity
WHERE day >= CURRENT_DATE - 30
GROUP BY
    service_id,
    service_name
ORDER BY log_count DESC;

### Before Optimization:
Execution Time: 0.363 ms


## Query - 2: `02_slowest_endpoints_from_mv.sql`
EXPLAIN ANALYZE
SELECT
    endpoint_id,
    endpoint_path,
    request_type,
    ROUND(
        SUM(total_response_time_ms)::numeric
        / NULLIF(SUM(request_count), 0),
        2
    ) AS avg_response_time_ms
FROM mv_daily_endpoint_latency
WHERE day >= CURRENT_DATE - 30
GROUP BY
    endpoint_id,
    endpoint_path,
    request_type
ORDER BY avg_response_time_ms DESC
LIMIT 20;

### Before Optimization:
Execution Time: 0.877 ms

## Query - 3: `03_status_code_distribution_from_mv.sql`
EXPLAIN ANALYZE
SELECT
    status_code,
    SUM(status_count) AS status_count
FROM mv_daily_status_code_distribution
WHERE day >= CURRENT_DATE - 30
GROUP BY status_code
ORDER BY status_code;

### Before Optimization:
Execution Time: 6.924 ms

# 2. OLAP

## Query - 1: `01_service_error_trend_from_olap.sql`
EXPLAIN ANALYZE
SELECT
    day,
    service_id,
    service_name,
    error_count
FROM mv_log_olap_daily
WHERE aggregation_level = 'day_service'
  AND day >= CURRENT_DATE - 30
ORDER BY day DESC, error_count DESC;

### Execution Time:
1.423 ms

## Query - 2: `02_log_level_trend_from_olap.sql`
EXPLAIN ANALYZE
SELECT
    day,
    log_level_id,
    level_name,
    request_count
FROM mv_log_olap_daily
WHERE aggregation_level = 'day_log_level'
  AND day >= CURRENT_DATE - 30
ORDER BY day DESC, request_count DESC;

### Execution Time:
1.733 ms

## Query - 3: `03_daily_total_from_olap.sql`
EXPLAIN ANALYZE
SELECT
    day,
    request_count,
    error_count,
    avg_response_time_ms
FROM mv_log_olap_daily
WHERE aggregation_level = 'day_total'
  AND day >= CURRENT_DATE - 30
ORDER BY day DESC;

### Execution Time:
0.829 ms

# 3. Indexing

## Query - 1: Before Creating indexes

EXPLAIN (ANALYZE, BUFFERS)
SELECT log_id, service_id, log_level_id, created_at, status_code
FROM logs
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
ORDER BY created_at DESC
LIMIT 100;

### Execution Time:
890.627

## Query - 2: After Creating Indexes

SELECT log_id, service_id, log_level_id, created_at, status_code
FROM logs
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
ORDER BY created_at DESC
LIMIT 100;

### Execution Time:
1.635 ms

## Query - 3: Composite index on service errors

EXPLAIN (ANALYZE, BUFFERS)
SELECT log_id, created_at, message, status_code
FROM logs
WHERE service_id = 1
  AND log_level_id = 4
ORDER BY created_at DESC
LIMIT 50;

### Execution Time:
0.544 ms

## Query - 4: Partial index on errors

EXPLAIN (ANALYZE, BUFFERS)
SELECT log_id, service_id, created_at, message
FROM logs
WHERE log_level_id IN (4, 5)
  AND service_id = 2
  AND created_at >= CURRENT_TIMESTAMP - INTERVAL '30 days'
ORDER BY created_at DESC;

### Execution Time:
221.92 ms

# 4.  Partitioning

## Query - 1: Partition pruning check

EXPLAIN (ANALYZE, BUFFERS)
SELECT log_id, service_id, log_level_id, created_at
FROM logs
WHERE created_at >= '2026-04-01'
  AND created_at < '2026-06-01'
ORDER BY created_at DESC
LIMIT 100;

### Execution Time:
486.017 ms

## Query -2: Cross partition query

EXPLAIN (ANALYZE, BUFFERS)
SELECT service_id, COUNT(*) AS log_count
FROM logs
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '60 days'
GROUP BY service_id
ORDER BY log_count DESC;

### Execution Time:
1394.995 ms

## Query - 3: Single partition error query

EXPLAIN (ANALYZE, BUFFERS)
SELECT service_id, COUNT(*) AS error_count
FROM logs
WHERE created_at >= '2024-06-01'
  AND created_at < '2024-08-01'
  AND log_level_id = 4
GROUP BY service_id
ORDER BY error_count DESC;

### Execution Time:
77.615 ms


## Query - 4: Flat vs Partition comparison

EXPLAIN (ANALYZE, BUFFERS)
SELECT service_id, COUNT(*) AS log_count
FROM logs_unpartitioned
WHERE created_at >= '2025-10-01'
  AND created_at < '2025-12-01'
GROUP BY service_id;

### Execution Time:
166.971 ms