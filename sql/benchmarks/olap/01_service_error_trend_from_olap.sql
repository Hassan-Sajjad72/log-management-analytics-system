EXPLAIN ANALYZE
SELECT
    day,
    service_id,
    service_name,
    error_count
FROM mv_log_olap_daily
WHERE aggregation_level = 'day_service'
  AND day >= CURRENT_DATE - 30
ORDER BY day DESC, error_count DESC;
