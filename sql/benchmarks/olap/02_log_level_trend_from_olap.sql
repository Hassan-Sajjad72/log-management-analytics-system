EXPLAIN ANALYZE
SELECT
    day,
    log_level_id,
    level_name,
    request_count
FROM mv_log_olap_daily
WHERE aggregation_level = 'day_log_level'
  AND day >= CURRENT_DATE - 30
ORDER BY day DESC, request_count DESC;
