CREATE TABLE logs (
    log_id BIGSERIAL PRIMARY KEY,
    request_id UUID NOT NULL,
    service_id INT NOT NULL REFERENCES services(service_id),
    server_id INT NOT NULL REFERENCES servers(server_id),
    user_id INT REFERENCES users(user_id),
    endpoint_id INT NOT NULL REFERENCES api_endpoints(endpoint_id),
    log_level_id INT NOT NULL REFERENCES log_levels(log_level_id),
    error_category_id INT REFERENCES error_categories(error_category_id),
    message TEXT NOT NULL,
    method VARCHAR(10),
    response_time_ms INT CHECK (response_time_ms >= 0),
    ip_address INET,
    status_code INT NOT NULL CHECK (status_code BETWEEN 100 AND 599),
    created_at TIMESTAMPTZ NOT NULL
);