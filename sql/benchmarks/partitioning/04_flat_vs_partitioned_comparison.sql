-- Run this against logs_unpartitioned (flat) for comparison
EXPLAIN (ANALYZE, BUFFERS)
SELECT service_id, COUNT(*) AS log_count
FROM logs_unpartitioned
WHERE created_at >= '2026-05-01'
  AND created_at < '2026-06-01'
GROUP BY service_id;