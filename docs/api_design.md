# API Design

Even before coding the backend, define the API surface so the data flow is clear.

## Endpoints

- `GET /logs`
- `GET /logs?service_id=1&level=ERROR`
- `GET /analytics/errors-by-service`
- `GET /analytics/slow-endpoints`
- `GET /analytics/daily-summary`
- `GET /benchmark/results`