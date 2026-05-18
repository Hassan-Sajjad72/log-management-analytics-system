-- Simulates concurrent inserts from multiple services.
-- Run this in two separate pgAdmin windows simultaneously to observe behavior.

-- This represents Service A inserting logs
BEGIN;
INSERT INTO logs (
    request_id, service_id, server_id, user_id, endpoint_id,
    log_level_id, message, method, response_time_ms,
    ip_address, status_code, created_at
) VALUES (
    gen_random_uuid(), 1, 1, NULL, 1,
    2, 'Concurrent insert test from Service A',
    'GET', 120, '10.0.0.1', 200, CURRENT_TIMESTAMP
);
COMMIT;

-- This represents Service B inserting logs
BEGIN;
INSERT INTO logs (
    request_id, service_id, server_id, user_id, endpoint_id,
    log_level_id, message, method, response_time_ms,
    ip_address, status_code, created_at
) VALUES (
    gen_random_uuid(), 2, 1, NULL, 1,
    3, 'Concurrent insert test from Service B',
    'POST', 150, '10.0.0.2', 201, CURRENT_TIMESTAMP
);
COMMIT;