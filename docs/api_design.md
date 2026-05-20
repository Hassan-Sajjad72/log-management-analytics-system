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