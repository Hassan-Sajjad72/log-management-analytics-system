-- Error analysis scoped to one month — benefits most from pruning
EXPLAIN (ANALYZE, BUFFERS)
SELECT service_id, COUNT(*) AS error_count
FROM logs
WHERE created_at >= '2024-06-01'
  AND created_at < '2024-08-01'
  AND log_level_id = 4
GROUP BY service_id
ORDER BY error_count DESC;