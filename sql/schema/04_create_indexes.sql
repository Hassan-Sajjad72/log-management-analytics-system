-- Indexes for the logs table.
-- Applied after data load to avoid slowing down bulk insertion.

-- Single-column index on created_at for time-range filtering
CREATE INDEX IF NOT EXISTS idx_log_created_at
    ON logs (created_at DESC);

-- For JSONB metadata searching
CREATE INDEX IF NOT EXISTS idx_logs_metadata ON logs USING gin(metadata);

-- Single-column index on log_level_id for severity filtering
CREATE INDEX IF NOT EXISTS idx_log_log_level_id
    ON logs (log_level_id);

-- Composite index: service + time (most common dashboard filter pattern)
CREATE INDEX IF NOT EXISTS idx_log_service_created_at
    ON logs (service_id, created_at DESC);

-- Composite index: service + log level (error analysis per service)
CREATE INDEX IF NOT EXISTS idx_log_service_log_level
    ON logs (service_id, log_level_id);

-- Partial index: only ERROR and CRITICAL rows (selective, smaller, faster)
CREATE INDEX IF NOT EXISTS idx_log_errors_only
    ON logs (service_id, created_at DESC)
    WHERE log_level_id IN (4, 5);