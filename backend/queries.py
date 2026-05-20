
def dashboard_summary_query():
    return """
        SELECT
            COUNT(*) AS total_logs,
            COUNT(*) FILTER (WHERE status_code >=500) AS server_errors,
            COUNT(*) FILTER (WHERE status_code >=400 AND status_code <500) AS client_errors,
            COUNT(*) FILTER (WHERE status_code >= 200 AND status_code <300) AS successful_requests,
            COUNT(*) FILTER (WHERE status_code >=300 AND status_code <400) AS redirects,
            COUNT(*) FILTER (WHERE status_code IS NULL) AS unknown_status,
            ROUND(AVG(response_time_ms), 2) AS avg_response_time
        FROM logs;
    """

def recent_logs_query():
    return """
        SELECT
            log_id,
            request_id,
            service_id,
            endpoint_id,
            status_code,
            response_time_ms,
            created_at
        FROM logs
        WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
        ORDER BY created_at DESC
        LIMIT 100;
    """

def errors_by_service_query():
    return """
        SELECT
            service_id,
            service_name,
            SUM(error_logs) AS error_count
        FROM mv_daily_service_activity
        GROUP BY
            service_id,
            service_name
        HAVING SUM(error_logs) > 0
        ORDER BY error_count DESC;
    """

def slowest_endpoints_query():
    return """
        SELECT
            endpoint_id,
            endpoint_path,
            request_type,
            ROUND(
                SUM(total_response_time_ms)::numeric
                / NULLIF(SUM(request_count), 0),
                2
            ) AS avg_response_time_ms
        FROM mv_daily_endpoint_latency
        GROUP BY
            endpoint_id,
            endpoint_path,
            request_type
        ORDER BY avg_response_time_ms DESC
        LIMIT 20;
    """

def status_code_distribution_query():
    return """
        SELECT
            status_code,
            SUM(status_count) AS status_count
        FROM mv_daily_status_code_distribution
        GROUP BY status_code
        ORDER BY status_code;
    """

def service_activity_query():
    return """
        SELECT
            service_id,
            service_name,
            SUM(total_logs) AS log_count,
            ROUND(
                SUM(total_response_time_ms)::numeric
                / NULLIF(SUM(total_logs), 0),
                2
            ) AS avg_response_time_ms
        FROM mv_daily_service_activity
        WHERE day >= CURRENT_DATE - 30
        GROUP BY
            service_id,
            service_name
        ORDER BY log_count DESC;
    """

def filtered_logs_query(filters):
    query = """
        SELECT
            l.log_id,
            l.created_at,
            s.service_name,
            ll.level_name,
            l.status_code,
            l.response_time_ms,
            l.message
        FROM logs l
        JOIN services s ON l.service_id = s.service_id
        JOIN log_levels ll ON l.log_level_id = ll.log_level_id
        WHERE 1=1
    """

    params = []

    if filters.get("service_id"):
        query += " AND l.service_id = %s"
        params.append(filters["service_id"])

    if filters.get("log_level_id"):
        query += " AND l.log_level_id = %s"
        params.append(filters["log_level_id"])

    if filters.get("status_code"):
        query += " AND l.status_code = %s"
        params.append(filters["status_code"])

    query += " ORDER BY l.created_at DESC LIMIT %s"
    params.append(filters.get("limit", 100))

    return query, params

def log_detail_query():
    return """
        SELECT
            l.*,
            s.service_name,
            sv.server_name,
            u.username,
            ae.endpoint_path,
            ae.request_type,
            ll.level_name,
            ec.category_name
        FROM logs l
        JOIN services s ON l.service_id = s.service_id
        JOIN servers sv ON l.server_id = sv.server_id
        LEFT JOIN users u ON l.user_id = u.user_id
        JOIN api_endpoints ae ON l.endpoint_id = ae.endpoint_id
        JOIN log_levels ll ON l.log_level_id = ll.log_level_id
        LEFT JOIN error_categories ec ON l.error_category_id = ec.error_category_id
        WHERE l.log_id = %s;
    """