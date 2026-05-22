# API Testing

## Tool Used

Browser and Flask local server.

## Tested Routes

| Route | Type | Purpose | Status |
|---|---|---|---|
| `/` | Page | Dashboard overview | Working |
| `/logs` | Page | View and filter logs | Working |
| `/analytics` | Page | Materialized view analytics | Working |
| `/analytics/olap` | Page | OLAP aggregation results | Working |
| `/techniques` | Page | DB technique explanation | Working |

## Tested Endpoints

| Endpoint | Method | Expected Result | Status |
|---|---|---|---|
| `/api/health` | GET | Backend health status | 200 |
| `/api/logs?limit=10` | GET | Latest 10 logs | 200 |
| `/api/logs/<log_id>` | GET | Single log detail | 200 |
| `/api/services` | GET | Services list | 200 |
| `/api/analytics/summary` | GET | Total logs and error counts | 200 |
| `/api/analytics/errors-by-service` | GET | Error count per service | 200 |
| `/api/analytics/endpoint-latency` | GET | Avg latency per endpoint | 200 |

## Analytics API Testing

| Endpoint | Uses | Expected |
|---|---|---|
| `/api/analytics/daily-service-activity` | `mv_daily_service_activity` | Daily service activity rows |
| `/api/analytics/daily-endpoint-latency` | `mv_daily_endpoint_latency` | Endpoint latency rows |
| `/api/analytics/status-code-distribution` | `mv_daily_status_code_distribution` | Status code distribution rows |
| `/api/analytics/olap/daily-totals` | `mv_log_olap_daily` | Daily total OLAP rows |
| `/api/analytics/olap/service-summary` | `mv_log_olap_daily` | Service-level OLAP rows |
| `/api/analytics/olap/endpoint-summary` | `mv_log_olap_daily` | Endpoint-level OLAP rows |