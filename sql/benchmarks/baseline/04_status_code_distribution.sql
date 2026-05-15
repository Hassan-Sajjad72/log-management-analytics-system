EXPLAIN ANALYZE
SELECT
    status_code,
    COUNT(*) AS status_count
FROM logs
GROUP BY status_code
ORDER BY status_code;