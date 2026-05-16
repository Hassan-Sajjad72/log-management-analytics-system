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
