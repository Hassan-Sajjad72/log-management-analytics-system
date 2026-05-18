-- Demonstrates row-level locking with SELECT FOR UPDATE.
-- Useful when updating a specific log record (e.g., flagging an incident).

-- Session: A
BEGIN;

-- Lock a specific log row for update
-- Session: B
SELECT log_id, message, status_code
FROM logs
WHERE log_id = 1000
FOR UPDATE;

-- Simulate processing delay (in real app, business logic runs here)

-- Update the row
UPDATE logs
SET message = message || ' [REVIEWED]'
WHERE log_id = 1000;

COMMIT;