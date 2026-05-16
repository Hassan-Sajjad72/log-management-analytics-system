EXPLAIN (ANALYZE, BUFFERS)
SELECT
    log_id,
    request_id,
    service_id,
    endpoint_id,
    status_code,
    response_time_ms,
    created_at
FROM logs
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY created_at DESC
LIMIT 100;
