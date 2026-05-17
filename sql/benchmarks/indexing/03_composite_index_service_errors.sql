-- Tests composite index: (service_id, log_level_id)
EXPLAIN (ANALYZE, BUFFERS)
SELECT log_id, created_at, message, status_code
FROM logs
WHERE service_id = 1
  AND log_level_id = 4
ORDER BY created_at DESC
LIMIT 50;