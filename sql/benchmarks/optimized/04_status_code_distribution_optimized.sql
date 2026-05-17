EXPLAIN (ANALYZE, BUFFERS)
SELECT
    status_code,
    SUM(status_count) AS status_count
FROM mv_daily_status_code_distribution
GROUP BY status_code
ORDER BY status_code;
