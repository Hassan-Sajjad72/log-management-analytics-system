-- Refresh analytics summaries after loading new log data.
-- Unique indexes created with the materialized views allow concurrent refreshes.

REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_service_activity;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_endpoint_latency;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_status_code_distribution;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_log_olap_daily;
