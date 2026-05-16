-- Materialized views for dashboard-style analytics over the logs fact table.
-- These sit on top of the logical logs table, so later partitioning/indexing
-- work can improve refresh speed without changing consumer queries.

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_service_activity AS
SELECT
    date_trunc('day', l.created_at)::date AS day,
    l.service_id,
    s.service_name,
    COUNT(*) AS total_logs,
    COUNT(*) FILTER (WHERE ll.level_name = 'ERROR') AS error_logs,
    SUM(l.response_time_ms) AS total_response_time_ms,
    ROUND(AVG(l.response_time_ms)::numeric, 2) AS avg_response_time_ms
FROM logs AS l
JOIN services AS s
    ON s.service_id = l.service_id
JOIN log_levels AS ll
    ON ll.log_level_id = l.log_level_id
GROUP BY
    date_trunc('day', l.created_at)::date,
    l.service_id,
    s.service_name
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_daily_service_activity_unique
    ON mv_daily_service_activity (day, service_id);

CREATE INDEX IF NOT EXISTS idx_mv_daily_service_activity_service_day
    ON mv_daily_service_activity (service_id, day DESC);


CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_endpoint_latency AS
SELECT
    date_trunc('day', l.created_at)::date AS day,
    l.endpoint_id,
    ae.endpoint_path,
    ae.request_type,
    COUNT(*) AS request_count,
    SUM(l.response_time_ms) AS total_response_time_ms,
    ROUND(AVG(l.response_time_ms)::numeric, 2) AS avg_response_time_ms,
    MAX(l.response_time_ms) AS max_response_time_ms
FROM logs AS l
JOIN api_endpoints AS ae
    ON ae.endpoint_id = l.endpoint_id
WHERE l.response_time_ms IS NOT NULL
GROUP BY
    date_trunc('day', l.created_at)::date,
    l.endpoint_id,
    ae.endpoint_path,
    ae.request_type
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_daily_endpoint_latency_unique
    ON mv_daily_endpoint_latency (day, endpoint_id);

CREATE INDEX IF NOT EXISTS idx_mv_daily_endpoint_latency_endpoint_day
    ON mv_daily_endpoint_latency (endpoint_id, day DESC);


CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_status_code_distribution AS
SELECT
    date_trunc('day', created_at)::date AS day,
    status_code,
    COUNT(*) AS status_count
FROM logs
GROUP BY
    date_trunc('day', created_at)::date,
    status_code
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_daily_status_code_distribution_unique
    ON mv_daily_status_code_distribution (day, status_code);

CREATE INDEX IF NOT EXISTS idx_mv_daily_status_code_distribution_day
    ON mv_daily_status_code_distribution (day DESC);
