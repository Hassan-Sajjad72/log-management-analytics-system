# API Testing

## Tool Used

Browser

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