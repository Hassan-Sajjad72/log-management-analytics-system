CREATE TABLE log_levels (
    log_level_id SERIAL PRIMARY KEY,
    level_name VARCHAR(50) NOT NULL UNIQUE
);
