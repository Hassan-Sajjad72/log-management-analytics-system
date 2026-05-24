from flask import Flask, render_template, request, jsonify, abort
import analytics_queries
from db import fetch_all, fetch_one, execute_command
import queries
import psycopg2

app = Flask(__name__)

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

@app.route('/')
def dashboard():
    summary = fetch_one(queries.dashboard_summary_query())
    recent_logs = fetch_all(queries.recent_logs_query(), (10,))

    return render_template(
        "dashboard.html",
        summary = summary,
        recent_logs = recent_logs
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

if __name__ == "__main__":
    app.run(debug=True)
