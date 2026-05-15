EXPLAIN ANALYZE
SELECT
    endpoint_id,
    AVG(response_time_ms) AS avg_response_time_ms
FROM logs
WHERE response_time_ms IS NOT NULL
GROUP BY endpoint_id
ORDER BY avg_response_time_ms DESC
LIMIT 20;