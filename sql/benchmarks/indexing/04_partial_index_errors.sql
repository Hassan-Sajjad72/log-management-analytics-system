-- Tests partial index (only ERROR/CRITICAL rows)
EXPLAIN (ANALYZE, BUFFERS)
SELECT log_id, service_id, created_at, message
FROM logs
WHERE log_level_id IN (4, 5)
  AND service_id = 2
  AND created_at >= CURRENT_TIMESTAMP - INTERVAL '30 days'
ORDER BY created_at DESC;