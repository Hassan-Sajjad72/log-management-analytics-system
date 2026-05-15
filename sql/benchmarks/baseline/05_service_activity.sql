EXPLAIN ANALYZE
SELECT
    service_id,
    COUNT(*) AS log_count
FROM logs
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY service_id
ORDER BY log_count DESC;