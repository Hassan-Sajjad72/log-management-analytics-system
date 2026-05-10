CREATE TABLE services (
    service_id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    owner_team VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);