-- Run this BEFORE creating indexes (drop them first if needed)
EXPLAIN (ANALYZE, BUFFERS)
SELECT log_id, service_id, log_level_id, created_at, status_code
FROM logs
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
ORDER BY created_at DESC
LIMIT 100;