-- Run this against logs_unpartitioned (flat) for comparison
EXPLAIN (ANALYZE, BUFFERS)
SELECT service_id, COUNT(*) AS log_count
FROM logs_unpartitioned
WHERE created_at >= '2025-10-01'
  AND created_at < '2025-12-01'
GROUP BY service_id;