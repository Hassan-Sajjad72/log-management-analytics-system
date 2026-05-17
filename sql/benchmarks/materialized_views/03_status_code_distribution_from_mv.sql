EXPLAIN ANALYZE
SELECT
    status_code,
    SUM(status_count) AS status_count
FROM mv_daily_status_code_distribution
WHERE day >= CURRENT_DATE - 30
GROUP BY status_code
ORDER BY status_code;
