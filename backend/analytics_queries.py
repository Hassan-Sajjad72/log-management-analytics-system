def daily_service_activity_query():
    return """
        SELECT
            day,
            service_id,
            service_name,
            total_logs,
            error_logs,
            avg_response_time_ms
        FROM mv_daily_service_activity
        ORDER BY day DESC, total_logs DESC
        LIMIT %s;
    """

def daily_endpoint_latency_query():
    return """
        SELECT
            day,
            endpoint_id,
            endpoint_path,
            request_type,
            request_count,
            avg_response_time_ms,
            max_response_time_ms
        FROM mv_daily_endpoint_latency
        ORDER BY day DESC, avg_response_time_ms DESC
        LIMIT %s;
    """


def daily_status_code_distribution_query():
    return """
        SELECT
            day,
            status_code,
            status_count
        FROM mv_daily_status_code_distribution
        ORDER BY day DESC, status_count DESC
        LIMIT %s;
    """


def olap_daily_totals_query():
    return """
        SELECT
            day,
            request_count,
            error_count,
            avg_response_time_ms
        FROM mv_log_olap_daily
        WHERE aggregation_level = 'day_total'
        ORDER BY day DESC
        LIMIT %s;
    """


def olap_service_summary_query():
    return """
        SELECT
            day,
            service_name,
            request_count,
            error_count,
            avg_response_time_ms
        FROM mv_log_olap_daily
        WHERE aggregation_level = 'day_service'
        ORDER BY day DESC, request_count DESC
        LIMIT %s;
    """


def olap_endpoint_summary_query():
    return """
        SELECT
            day,
            endpoint_path,
            request_type,
            request_count,
            avg_response_time_ms
        FROM mv_log_olap_daily
        WHERE aggregation_level = 'day_endpoint'
        ORDER BY day DESC, avg_response_time_ms DESC
        LIMIT %s;
    """


def olap_log_level_summary_query():
    return """
        SELECT
            day,
            level_name,
            request_count,
            error_count
        FROM mv_log_olap_daily
        WHERE aggregation_level = 'day_log_level'
        ORDER BY day DESC, request_count DESC
        LIMIT %s;
    """


def refresh_materialized_views_queries():
    return [
        "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_service_activity;",
        "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_endpoint_latency;",
        "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_status_code_distribution;",
        "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_log_olap_daily;"
    ]