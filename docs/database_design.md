# Database Design

## Tables and purpose

- `services`: Reference table for application services producing logs .
- `servers`: Reference table for virtual servers.
- `users`: Reference table for application users.
- `api_endpoints`: Reference table for API endpoints.
- `log_levels`: Reference table for log severity levels.
- `error_categories`: Reference table categorizing errors.
- `logs`: Central fact table containing each log event with the following key columns:
	- `log_id` (PK)
	- `service_id` (FK -> services)
	- `server_id` (FK -> servers)
	- `user_id` (FK -> users)
	- `endpoint_id` (FK -> api_endpoints)
	- `log_level_id` (FK -> log_levels)
	- `error_category_id` (FK -> error_categories)
	- `message`, `response_time_ms`, `ip_address`, `status_code`, `created_at`

## Relationships

- `logs.service_id` -> `services.service_id` (many logs per service)
- `logs.server_id` -> `servers.server_id` (many logs per server)
- `logs.user_id` -> `users.user_id` (many logs may reference a user)
- `logs.endpoint_id` -> `api_endpoints.endpoint_id` (many logs per endpoint)
- `logs.log_level_id` -> `log_levels.log_level_id` (many logs per log level)
- `logs.error_category_id` -> `error_categories.error_category_id` (many logs per error category)

These are many-to-one relationships from `logs` to each reference table; `logs` is the central fact table.

## ERD image

Included an ERD image from `docs/images/erd.svg`

![ERD](images/erd.svg)
