from flask import Flask, render_template, request, jsonify, abort
from db import fetch_all, fetch_one
import queries

app = Flask(__name__)

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
    services = fetch_all(queries.services_query())
    log_levels = fetch_all(queries.log_levels_query())

    filters = {
        "service_id": request.args.get("service_id"),
        "log_level_id": request.args.get("log_level_id"),
        "status_code": request.args.get("status_code"),
        "limit": int(request.args.get("limit", 100))
    }

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
    log = fetch_one(queries.log_detail_query(), (log_id))

    if not log:
        abort(404)
    
    return render_template("log_detail.html", log=log)

@app.route("/services")
def services():
    services_data = fetch_all(queries.services_query())
    return render_template("services.html", services=services_data)

@app.route("/analytics")
def analytics():
    errors_by_service = fetch_all(queries.errors_by_service_query())
    endpoint_latency = fetch_all(queries.endpoint_latency_query())

    return render_template(
        "analytics.html",
        errors_by_service=errors_by_service,
        endpoint_latency=endpoint_latency
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
    filters = {
        "service_id": request.args.get("service_id"),
        "log_level_id": request.args.get("log_level_id"),
        "status_code": request.args.get("status_code"),
        "limit": int(request.args.get("limit", 100))
    }

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


if __name__ == "__main__":
    app.run(debug=True)