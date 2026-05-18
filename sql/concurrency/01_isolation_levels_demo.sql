-- Demonstrates READ COMMITTED vs REPEATABLE READ isolation levels.
-- READ COMMITTED (PostgreSQL default): each statement sees latest committed data.
-- REPEATABLE READ: entire transaction sees a consistent snapshot from its start.

-- Session A: Start a transaction and read error count
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

SELECT COUNT(*) AS error_count_at_start
FROM logs
WHERE log_level_id = 4;

-- Session B: Insert new error logs
INSERT INTO logs (
    request_id,
    service_id,
    server_id,
    endpoint_id,
    log_level_id,
    message,
    status_code,
    created_at,
    method
) VALUES (
    gen_random_uuid(),
    1,     
    1,     
    1,     
    4,  
    'New error log for isolation test',
    500,
    NOW(),
    'POST'
);

-- Verify the insert
SELECT COUNT(*) AS error_count_after_insert FROM logs WHERE log_level_id = 4;

-- Session A: Check error count again
SELECT COUNT(*) AS error_count_after_insert
FROM logs
WHERE log_level_id = 4;
-- With REPEATABLE READ: count will be the same as above (snapshot isolation)

-- With READ COMMITTED: count would increase (sees new commits)
-- Session A: using READ COMMITTED

SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT COUNT(*) AS error_count_after_insert_read_committed
FROM logs
WHERE log_level_id = 4;


-- Session A: Commit the transaction

COMMIT;