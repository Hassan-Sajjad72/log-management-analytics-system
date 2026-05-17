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