-- Partitioned version of the logs table.
-- Range partitioned by created_at, monthly partitions for 90-day data window.
-- The primary key includes created_at because PostgreSQL requires the partition
-- key to be part of every unique constraint on a partitioned table.

-- Step 1: Rename the existing flat table as backup
ALTER TABLE logs RENAME TO logs_unpartitioned;

-- Step 2: Create the new partitioned parent table
CREATE TABLE logs (
    log_id      BIGSERIAL,
    request_id  UUID NOT NULL,
    service_id  INT NOT NULL REFERENCES services(service_id),
    server_id   INT NOT NULL REFERENCES servers(server_id),
    user_id     INT REFERENCES users(user_id),
    endpoint_id INT NOT NULL REFERENCES api_endpoints(endpoint_id),
    log_level_id INT NOT NULL REFERENCES log_levels(log_level_id),
    error_category_id INT REFERENCES error_categories(error_category_id),
    message     TEXT NOT NULL,
    method      VARCHAR(10),
    response_time_ms INT CHECK (response_time_ms >= 0),
    ip_address  INET,
    status_code INT NOT NULL CHECK (status_code BETWEEN 100 AND 599),
    metadata JSONB,
    created_at  TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (log_id, created_at)
) PARTITION BY RANGE (created_at);

-- Step 3: Create monthly partitions covering the 90-day data window
-- Your generator uses: fake.date_time_between(start_date='-90d', end_date='now')
-- So you need partitions from ~3 months ago to current month

CREATE TABLE logs_2024_01 PARTITION OF logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE logs_2024_02 PARTITION OF logs
    FOR VALUES FROM ('2024-02-01') TO ('2024-04-01');

CREATE TABLE logs_2024_04 PARTITION OF logs
    FOR VALUES FROM ('2024-04-01') TO ('2024-06-01');

CREATE TABLE logs_2024_06 PARTITION OF logs
    FOR VALUES FROM ('2024-06-01') TO ('2024-08-01');

CREATE TABLE logs_2024_08 PARTITION OF logs
    FOR VALUES FROM ('2024-08-01') TO ('2024-10-01');

CREATE TABLE logs_2024_10 PARTITION OF logs
    FOR VALUES FROM ('2024-10-01') TO ('2024-12-01');

CREATE TABLE logs_2024_12 PARTITION OF logs
    FOR VALUES FROM ('2024-12-01') TO ('2025-02-01');

CREATE TABLE logs_2025_02 PARTITION OF logs
    FOR VALUES FROM ('2025-02-01') TO ('2025-04-01');

CREATE TABLE logs_2025_03 PARTITION OF logs
    FOR VALUES FROM ('2025-04-01') TO ('2025-06-01');

CREATE TABLE logs_2025_04 PARTITION OF logs
    FOR VALUES FROM ('2025-06-01') TO ('2025-08-01');

CREATE TABLE logs_2025_05 PARTITION OF logs
    FOR VALUES FROM ('2025-08-01') TO ('2025-10-01');

CREATE TABLE logs_2025_06 PARTITION OF logs
    FOR VALUES FROM ('2025-10-01') TO ('2025-12-01');

CREATE TABLE logs_2026_01 PARTITION OF logs
    FOR VALUES FROM ('2025-12-01') TO ('2026-02-01');

CREATE TABLE logs_2026_02 PARTITION OF logs
    FOR VALUES FROM ('2026-02-01') TO ('2026-04-01');

CREATE TABLE logs_2026_03 PARTITION OF logs
    FOR VALUES FROM ('2026-04-01') TO ('2026-06-01');

CREATE TABLE logs_2026_04 PARTITION OF logs
    FOR VALUES FROM ('2026-06-01') TO ('2026-08-01');

CREATE TABLE logs_2026_05 PARTITION OF logs
    FOR VALUES FROM ('2026-08-01') TO ('2026-10-01');

CREATE TABLE logs_2026_06 PARTITION OF logs
    FOR VALUES FROM ('2026-10-01') TO ('2026-12-01');

-- Default partition catches anything outside defined ranges
CREATE TABLE logs_default PARTITION OF logs DEFAULT;

-- Step 4: Migrate data from flat table into partitioned table
INSERT INTO logs SELECT * FROM logs_unpartitioned;

-- Step 5: Verify row counts match
-- SELECT COUNT(*) FROM logs;
-- SELECT COUNT(*) FROM logs_unpartitioned;

-- Step 6: Drop flat table after verifying
-- DROP TABLE logs_unpartitioned;