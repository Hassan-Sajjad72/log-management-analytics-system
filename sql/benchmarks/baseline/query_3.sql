EXPLAIN ANALYZE
SELECT
    service_id,
    COUNT(*)
FROM logs
WHERE log_level_id = 3
GROUP BY service_id
ORDER BY COUNT(*) DESC;