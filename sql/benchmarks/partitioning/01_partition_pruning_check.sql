-- Shows partition pruning in action.
-- EXPLAIN output should show only 1-2 partitions scanned, not all.
EXPLAIN (ANALYZE, BUFFERS)
SELECT log_id, service_id, log_level_id, created_at
FROM logs
WHERE created_at >= '2026-04-01'
  AND created_at < '2026-06-01'
ORDER BY created_at DESC
LIMIT 100;