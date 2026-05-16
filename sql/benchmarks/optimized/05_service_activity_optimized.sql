EXPLAIN (ANALYZE, BUFFERS)
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
