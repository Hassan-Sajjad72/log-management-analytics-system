CREATE TABLE api_endpoints (
    endpoint_id SERIAL PRIMARY KEY,
    endpoint_path VARCHAR(255),
    request_type VARCHAR(20)
    UNIQUE(endpoint_path, request_type)
);