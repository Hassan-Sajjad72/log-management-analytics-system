# Baseline Query Results

## 01_recent_logs

## Purpose
Fetch the most recent logs from the last 24 hours.

## SQL Query
```sql
EXPLAIN ANALYZE
SELECT *
FROM logs
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC
LIMIT 100;
```

## Before Optimization
Execution time: 0.081 ms

## 02_errors_by_service

## Purpose
Count ERROR logs grouped by service.

## SQL Query
```sql
EXPLAIN ANALYZE
SELECT
	service_id,
	COUNT(*) AS error_count
FROM logs
WHERE log_level_id = (
	SELECT log_level_id
	FROM log_levels
	WHERE level_name = 'ERROR'
)
GROUP BY service_id
ORDER BY error_count DESC;
```

## Before Optimization
Execution time: 0.093 ms

## 03_slowest_endpoints

## Purpose
Find the slowest endpoints by average response time.

## SQL Query
```sql
EXPLAIN ANALYZE
SELECT
	endpoint_id,
	AVG(response_time_ms) AS avg_response_time_ms
FROM logs
WHERE response_time_ms IS NOT NULL
GROUP BY endpoint_id
ORDER BY avg_response_time_ms DESC
LIMIT 20;
```

## Before Optimization
Execution time: 1.032 ms

## 04_status_code_distribution

## Purpose
Show the distribution of logs across HTTP status codes.

## SQL Query
```sql
EXPLAIN ANALYZE
SELECT
	status_code,
	COUNT(*) AS status_count
FROM logs
GROUP BY status_code
ORDER BY status_code;
```

## Before Optimization
Execution time: 0.052 ms

## 05_service_activity

## Purpose
Measure service activity over the last 30 days.

## SQL Query
```sql
EXPLAIN ANALYZE
SELECT
	service_id,
	COUNT(*) AS log_count
FROM logs
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY service_id
ORDER BY log_count DESC;
```

## Before Optimization
Execution time: 0.078 ms