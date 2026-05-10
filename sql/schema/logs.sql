CREATE TABLE logs (
    log_id BIGSERIAL PRIMARY KEY,
    service_id INT REFERENCES services(service_id),
    server_id INT REFERENCES servers(server_id),
    user_id INT REFERENCES users(user_id),
    endpoint_id INT REFERENCES api_endpoints(endpoint_id),
    log_level_id INT REFERENCES log_levels(log_level_id),
    error_category_id INT REFERENCES error_categories(error_category_id),
    message TEXT,
    response_time_ms INT,
    ip_address INET,
    status_code INT,
    created_at TIMESTAMP
);