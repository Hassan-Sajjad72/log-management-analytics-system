EXPLAIN ANALYZE
SELECT
    endpoint_id,
    AVG(response_time_ms)
FROM logs
GROUP BY endpoint_id;