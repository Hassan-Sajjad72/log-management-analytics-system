-- Cross-partition query (spans multiple months)
-- Compare this to the same query on the flat table
EXPLAIN (ANALYZE, BUFFERS)
SELECT service_id, COUNT(*) AS log_count
FROM logs
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '60 days'
GROUP BY service_id
ORDER BY log_count DESC;