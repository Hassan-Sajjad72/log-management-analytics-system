EXPLAIN (ANALYZE, BUFFERS)
SELECT
    l.log_id,
    l.created_at,
    s.service_name,
    ll.level_name,
    l.status_code,
    l.response_time_ms,
    l.message
FROM logs l
JOIN services s ON l.service_id = s.service_id
JOIN log_levels ll ON l.log_level_id = ll.log_level_id
WHERE l.created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
ORDER BY l.created_at DESC
LIMIT %s;
