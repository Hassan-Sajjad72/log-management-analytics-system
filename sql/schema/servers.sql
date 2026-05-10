CREATE TABLE servers (
    server_id SERIAL PRIMARY KEY,
    server_name VARCHAR(255) NOT NULL,
    region VARCHAR(255),
    operating_system VARCHAR(255)
);