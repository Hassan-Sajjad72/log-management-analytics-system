# API Design

Even before coding the backend, define the API surface so the data flow is clear.

## Endpoints

- `GET /api/health`
- `GET /api/logs?limit=10`
- `GET /api/logs/<log_id>`
- `GET /api/services`
- `GET /api/analytics/summary`
- `GET /api/analytics/errors-by-service`
- `GET /api/analytics/endpoint-latency`

## Examples (curl)

Health check:

```bash
curl -s http://127.0.0.1:5000/api/health
# expected: { "status": "ok" }
```

Fetch recent logs (with query params):

```bash
curl -s "http://127.0.0.1:5000/api/logs?limit=5&status_code=500"
# expected: JSON array of log objects with fields like log_id, created_at, service_name, level_name, status_code, response_time_ms, message
```

Fetch analytics summary:

```bash
curl -s http://127.0.0.1:5000/api/analytics/summary | jq
# expected: { "total_logs": 12345, "avg_response_time_ms": 2345.6, ... }
```

Include pagination details and examples in `docs/api_testing.md` for test scripts and postman collections.