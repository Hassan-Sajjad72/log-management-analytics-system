EXPLAIN ANALYZE
SELECT
    service_id,
    COUNT(*) AS error_count
FROM logs
WHERE log_level_id = (
    SELECT log_level_id
    FROM log_levels
    WHERE level_name = 'ERROR'
)
GROUP BY service_id
ORDER BY error_count DESC;