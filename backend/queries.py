
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
        WHERE l.created_at >= CURRENT_TIMESTAMP - INTERVAL '30 days'
        ORDER BY l.created_at DESC
        LIMIT %s;
    """

def services_query():
    return """
        SELECT service_id, service_name, owner_team
        FROM services
        ORDER BY service_id;
    """


def log_levels_query():
    return """
        SELECT log_level_id, level_name
        FROM log_levels
        ORDER BY log_level_id;
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

def endpoint_latency_query():
    return """
        SELECT
            ae.endpoint_path,
            ROUND(AVG(l.response_time_ms), 2) AS avg_latency
        FROM logs l
        JOIN api_endpoints ae ON l.endpoint_id = ae.endpoint_id
        GROUP BY ae.endpoint_path
        ORDER BY avg_latency DESC
        LIMIT 10;
    """