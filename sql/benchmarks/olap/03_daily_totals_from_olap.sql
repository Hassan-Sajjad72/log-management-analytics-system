EXPLAIN ANALYZE
SELECT
    day,
    request_count,
    error_count,
    avg_response_time_ms
FROM mv_log_olap_daily
WHERE aggregation_level = 'day_total'
  AND day >= CURRENT_DATE - 30
ORDER BY day DESC;
