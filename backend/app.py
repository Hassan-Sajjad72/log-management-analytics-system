from flask import Flask, render_template, request, jsonify, abort, session, redirect, url_for
import analytics_queries
from db import fetch_all, fetch_one, execute_command
import queries
import psycopg2
import re
import os
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

TEAMS = [
    {"id": "Admin",          "label": "Admin",          "icon": "shield",   "color": "#6366f1", "desc": "Full access to all logs and analytics"},
    {"id": "Frontend Team",  "label": "Frontend Team",  "icon": "monitor",  "color": "#06b6d4", "desc": "Can only see logs from frontend services"},
    {"id": "Backend Team",   "label": "Backend Team",   "icon": "server",   "color": "#10b981", "desc": "Can only see logs from backend services"},
    {"id": "Database Team",  "label": "Database Team",  "icon": "database", "color": "#f59e0b", "desc": "Can only see logs from database services"},
]

def get_current_team():
    return session.get('team', None)

def require_admin():
    """Returns a redirect response if user is not Admin, else None."""
    team = get_current_team()
    if team != 'Admin':
        return render_template('forbidden.html', team=team), 403
    return None

MAX_LIMIT = 500

def wants_json_response():
    return request.path.startswith("/api/")

def parse_int_arg(name, default=None, minimum=None, maximum=None):
    raw_value = request.args.get(name)

    if raw_value in (None, ""):
        return default

    try:
        value = int(raw_value)
    except ValueError:
        raise ValueError(f"{name} must be a number.")

    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be at least {minimum}.")

    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be at most {maximum}.")

    return value

def log_filters_from_request(default_limit=100):
    return {
        "service_id": parse_int_arg("service_id", minimum=1),
        "log_level_id": parse_int_arg("log_level_id", minimum=1),
        "status_code": parse_int_arg("status_code", minimum=100, maximum=599),
        "limit": parse_int_arg("limit", default_limit, minimum=1, maximum=MAX_LIMIT)
    }

def limit_from_request(default_limit=50):
    return parse_int_arg("limit", default_limit, minimum=1, maximum=MAX_LIMIT)

@app.errorhandler(ValueError)
def handle_validation_error(error):
    message = str(error)
    if wants_json_response():
        return jsonify({"error": message}), 400

    return render_template(
        "error.html",
        title="Invalid request",
        message=message,
        status_code=400
    ), 400

@app.errorhandler(psycopg2.Error)
def handle_database_error(error):
    message = "The database request failed. Please check that PostgreSQL is running and required tables or views exist."
    detail = error.pgerror or str(error)

    if wants_json_response():
        return jsonify({"error": message, "detail": detail}), 503

    return render_template(
        "error.html",
        title="Database unavailable",
        message=message,
        detail=detail,
        status_code=503
    ), 503

@app.errorhandler(404)
def handle_not_found(error):
    if wants_json_response():
        return jsonify({"error": "Resource not found"}), 404

    return render_template(
        "error.html",
        title="Not found",
        message="The requested page or record was not found.",
        status_code=404
    ), 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            error = 'Please enter both email and password.'
        else:
            user = fetch_one(
                "SELECT user_id, email, password_hash, full_name, team FROM team_users WHERE email = %s",
                (email,)
            )
            if user and check_password_hash(user['password_hash'], password):
                session['team'] = user['team']
                session['user_name'] = user['full_name']
                session['user_email'] = user['email']
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid email or password.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def dashboard():
    if not get_current_team():
        return redirect(url_for('login'))
    summary = fetch_one(queries.dashboard_summary_query())
    recent_logs = fetch_all(queries.recent_logs_query(), (10,))

    return render_template(
        "dashboard.html",
        summary = summary,
        recent_logs = recent_logs,
        current_team = get_current_team()
    )

@app.route('/logs')
def logs():
    filters = log_filters_from_request()

    services = fetch_all(queries.services_query())
    log_levels = fetch_all(queries.log_levels_query())

    query, params = queries.filtered_logs_query(filters)
    logs_data = fetch_all(query, params)

    return render_template(
        "logs.html",
        logs=logs_data,
        services=services,
        log_levels=log_levels,
        filters=filters
    )

@app.route('/logs/<int:log_id>')
def log_detail(log_id):
    log = fetch_one(queries.log_detail_query(), (log_id,))

    if not log:
        abort(404)
    
    return render_template("log_detail.html", log=log)

@app.route("/services")
def services():
    services_data = fetch_all(queries.services_query())
    return render_template("services.html", services=services_data)

@app.route("/analytics")
def analytics():
    guard = require_admin()
    if guard: return guard

    service_activity = fetch_all(
        analytics_queries.daily_service_activity_query(),
        (20,)
    )

    endpoint_latency = fetch_all(
        analytics_queries.daily_endpoint_latency_query(),
        (20,)
    )

    status_distribution = fetch_all(
        analytics_queries.daily_status_code_distribution_query(),
        (20,)
    )

    return render_template(
        "analytics.html",
        service_activity=service_activity,
        endpoint_latency=endpoint_latency,
        status_distribution=status_distribution
    )

@app.route("/analytics/olap")
def olap():
    guard = require_admin()
    if guard: return guard

    daily_totals = fetch_all(
        analytics_queries.olap_daily_totals_query(),
        (20,)
    )

    service_summary = fetch_all(
        analytics_queries.olap_service_summary_query(),
        (20,)
    )

    endpoint_summary = fetch_all(
        analytics_queries.olap_endpoint_summary_query(),
        (20,)
    )

    log_level_summary = fetch_all(
        analytics_queries.olap_log_level_summary_query(),
        (20,)
    )

    return render_template(
        "olap.html",
        daily_totals=daily_totals,
        service_summary=service_summary,
        endpoint_summary=endpoint_summary,
        log_level_summary=log_level_summary
    )

@app.route("/analytics/refresh", methods=["POST"])
def refresh_analytics():
    guard = require_admin()
    if guard: return guard

    refresh_queries = analytics_queries.refresh_materialized_views_queries()

    for query in refresh_queries:
        execute_command(query)

    return render_template(
        "refresh_success.html",
        message="Materialized views refreshed successfully."
    )

@app.route("/benchmarks")
def benchmarks():
    return render_template("benchmarks.html")


@app.route("/techniques")
def techniques():
    return render_template("techniques.html")


@app.route("/api/health")
def api_health():
    return jsonify({"status": "ok"})

@app.route("/api/logs")
def api_logs():
    filters = log_filters_from_request()

    query, params = queries.filtered_logs_query(filters)
    logs_data = fetch_all(query, params)

    return jsonify(logs_data)


@app.route("/api/logs/<int:log_id>")
def api_log_detail(log_id):
    log = fetch_one(queries.log_detail_query(), (log_id,))

    if not log:
        return jsonify({"error": "Log not found"}), 404

    return jsonify(log)


@app.route("/api/services")
def api_services():
    services_data = fetch_all(queries.services_query())
    return jsonify(services_data)


@app.route("/api/analytics/summary")
def api_analytics_summary():
    summary = fetch_one(queries.dashboard_summary_query())
    return jsonify(summary)

@app.route("/api/dashboard/recent-logs")
def api_dashboard_recent_logs():
    limit = limit_from_request(10)
    data = fetch_all(queries.recent_logs_query(), (limit,))
    return jsonify(data)

@app.route("/api/dashboard/live")
def api_dashboard_live():
    limit = limit_from_request(12)
    after_log_id = parse_int_arg("after_log_id", 0, minimum=0)

    summary = fetch_one(queries.dashboard_summary_query())
    recent_logs = fetch_all(queries.recent_logs_query(), (limit,))
    new_logs = fetch_one(queries.new_logs_count_query(), (after_log_id,))

    return jsonify({
        "summary": summary,
        "recent_logs": recent_logs,
        "new_log_count": new_logs["new_log_count"]
    })


@app.route("/api/analytics/errors-by-service")
def api_errors_by_service():
    data = fetch_all(queries.errors_by_service_query())
    return jsonify(data)


@app.route("/api/analytics/endpoint-latency")
def api_endpoint_latency():
    data = fetch_all(queries.endpoint_latency_query())
    return jsonify(data)

@app.route("/api/analytics/daily-service-activity")
def api_daily_service_activity():
    limit = limit_from_request()
    data = fetch_all(
        analytics_queries.daily_service_activity_query(),
        (limit,)
    )
    return jsonify(data)


@app.route("/api/analytics/daily-endpoint-latency")
def api_daily_endpoint_latency():
    limit = limit_from_request()
    data = fetch_all(
        analytics_queries.daily_endpoint_latency_query(),
        (limit,)
    )
    return jsonify(data)


@app.route("/api/analytics/status-code-distribution")
def api_status_code_distribution():
    limit = limit_from_request()
    data = fetch_all(
        analytics_queries.daily_status_code_distribution_query(),
        (limit,)
    )
    return jsonify(data)


@app.route("/api/analytics/olap/daily-totals")
def api_olap_daily_totals():
    limit = limit_from_request()
    data = fetch_all(
        analytics_queries.olap_daily_totals_query(),
        (limit,)
    )
    return jsonify(data)


@app.route("/api/analytics/olap/service-summary")
def api_olap_service_summary():
    limit = limit_from_request()
    data = fetch_all(
        analytics_queries.olap_service_summary_query(),
        (limit,)
    )
    return jsonify(data)


@app.route("/api/analytics/olap/endpoint-summary")
def api_olap_endpoint_summary():
    limit = limit_from_request()
    data = fetch_all(
        analytics_queries.olap_endpoint_summary_query(),
        (limit,)
    )
    return jsonify(data)

@app.route("/api/benchmarks/custom-query", methods=["POST"])
def api_benchmarks_custom_query():
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "Missing query parameter"}), 400
        
    user_query = data["query"].strip()
    
    if not user_query.upper().startswith("SELECT"):
        return jsonify({"error": "Only SELECT queries are allowed."}), 400
        
    partitioned_query = user_query
    unpartitioned_query = re.sub(r'(?i)\bFROM\s+logs\b', 'FROM logs_unpartitioned', user_query)
    
    if unpartitioned_query == partitioned_query:
        return jsonify({"error": "The query must select FROM the 'logs' table to run this benchmark."}), 400
        
    explain_part = f"EXPLAIN (ANALYZE, FORMAT JSON) {partitioned_query}"
    explain_unpart = f"EXPLAIN (ANALYZE, FORMAT JSON) {unpartitioned_query}"
    
    try:
        unpart_res = fetch_one(explain_unpart)
        unpart_plan = unpart_res['QUERY PLAN'][0]
        unpart_time = unpart_plan.get('Execution Time', 0)
        
        part_res = fetch_one(explain_part)
        part_plan = part_res['QUERY PLAN'][0]
        part_time = part_plan.get('Execution Time', 0)
        
        return jsonify({
            "unpartitioned_ms": unpart_time,
            "partitioned_ms": part_time,
            "query": user_query
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
