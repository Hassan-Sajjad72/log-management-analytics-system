-- OLAP-style daily summary using GROUPING SETS.
-- This provides multiple useful rollups from one summary object without the
-- row explosion that would come from a full CUBE across every dimension.
-- The view is recreated so its schema can evolve safely during development.

DROP MATERIALIZED VIEW IF EXISTS mv_log_olap_daily;

CREATE MATERIALIZED VIEW mv_log_olap_daily AS
SELECT
    date_trunc('day', l.created_at)::date AS day,
    l.service_id,
    s.service_name,
    l.endpoint_id,
    ae.endpoint_path,
    ae.request_type,
    l.log_level_id,
    ll.level_name,
    l.status_code,
    COALESCE(l.service_id, -1) AS service_key,
    COALESCE(l.endpoint_id, -1) AS endpoint_key,
    COALESCE(l.log_level_id, -1) AS log_level_key,
    COALESCE(l.status_code, -1) AS status_code_key,
    COUNT(*) AS request_count,
    COUNT(*) FILTER (WHERE ll.level_name = 'ERROR') AS error_count,
    SUM(l.response_time_ms) AS total_response_time_ms,
    ROUND(AVG(l.response_time_ms)::numeric, 2) AS avg_response_time_ms,
    CASE
        WHEN GROUPING(l.service_id) = 0
            AND GROUPING(l.endpoint_id) = 1
            AND GROUPING(l.log_level_id) = 1
            AND GROUPING(l.status_code) = 1
            THEN 'day_service'
        WHEN GROUPING(l.service_id) = 1
            AND GROUPING(l.endpoint_id) = 0
            AND GROUPING(l.log_level_id) = 1
            AND GROUPING(l.status_code) = 1
            THEN 'day_endpoint'
        WHEN GROUPING(l.service_id) = 1
            AND GROUPING(l.endpoint_id) = 1
            AND GROUPING(l.log_level_id) = 0
            AND GROUPING(l.status_code) = 1
            THEN 'day_log_level'
        WHEN GROUPING(l.service_id) = 1
            AND GROUPING(l.endpoint_id) = 1
            AND GROUPING(l.log_level_id) = 1
            AND GROUPING(l.status_code) = 0
            THEN 'day_status_code'
        WHEN GROUPING(l.service_id) = 0
            AND GROUPING(l.endpoint_id) = 1
            AND GROUPING(l.log_level_id) = 0
            AND GROUPING(l.status_code) = 1
            THEN 'day_service_log_level'
        WHEN GROUPING(l.service_id) = 1
            AND GROUPING(l.endpoint_id) = 1
            AND GROUPING(l.log_level_id) = 1
            AND GROUPING(l.status_code) = 1
            THEN 'day_total'
        ELSE 'other'
    END AS aggregation_level
FROM logs AS l
JOIN services AS s
    ON s.service_id = l.service_id
JOIN api_endpoints AS ae
    ON ae.endpoint_id = l.endpoint_id
JOIN log_levels AS ll
    ON ll.log_level_id = l.log_level_id
GROUP BY GROUPING SETS (
    (
        date_trunc('day', l.created_at)::date
    ),
    (
        date_trunc('day', l.created_at)::date,
        l.service_id,
        s.service_name
    ),
    (
        date_trunc('day', l.created_at)::date,
        l.endpoint_id,
        ae.endpoint_path,
        ae.request_type
    ),
    (
        date_trunc('day', l.created_at)::date,
        l.log_level_id,
        ll.level_name
    ),
    (
        date_trunc('day', l.created_at)::date,
        l.status_code
    ),
    (
        date_trunc('day', l.created_at)::date,
        l.service_id,
        s.service_name,
        l.log_level_id,
        ll.level_name
    )
)
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_log_olap_daily_unique
    ON mv_log_olap_daily (
        day,
        aggregation_level,
        service_key,
        endpoint_key,
        log_level_key,
        status_code_key
    );

CREATE INDEX IF NOT EXISTS idx_mv_log_olap_daily_level_day
    ON mv_log_olap_daily (aggregation_level, day DESC);
