-- Master schema file for setting up the database in dependency order.

CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS services (
    service_id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL UNIQUE,
    owner_team VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS log_levels (
    log_level_id SERIAL PRIMARY KEY,
    level_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS error_categories (
    error_category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS servers (
    server_id SERIAL PRIMARY KEY,
    server_name VARCHAR(255) NOT NULL UNIQUE,
    region VARCHAR(255),
    operating_system VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS api_endpoints (
    endpoint_id SERIAL PRIMARY KEY,
    endpoint_path VARCHAR(255) NOT NULL,
    request_type VARCHAR(20) NOT NULL,
    UNIQUE(endpoint_path, request_type)
);

CREATE TABLE IF NOT EXISTS logs (
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
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL
);
