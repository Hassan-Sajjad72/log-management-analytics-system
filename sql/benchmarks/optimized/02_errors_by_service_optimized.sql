EXPLAIN (ANALYZE, BUFFERS)
SELECT
    service_id,
    service_name,
    SUM(error_logs) AS error_count
FROM mv_daily_service_activity
GROUP BY
    service_id,
    service_name
HAVING SUM(error_logs) > 0
ORDER BY error_count DESC;
