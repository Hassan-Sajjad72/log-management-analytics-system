-- Shows how consistent lock ordering prevents deadlocks.
-- If two transactions always lock resources in the same order,
-- circular waits (deadlocks) cannot occur.

-- SAFE: Both transactions access service_id=1 before service_id=2
-- Transaction 1: Session A
BEGIN;
SELECT * FROM services WHERE service_id = 1 FOR UPDATE;
SELECT * FROM services WHERE service_id = 2 FOR UPDATE;
-- do work
COMMIT;

-- Transaction 2 (same order = no deadlock possible): Session B
BEGIN;
SELECT * FROM services WHERE service_id = 1 FOR UPDATE;
SELECT * FROM services WHERE service_id = 2 FOR UPDATE;
COMMIT;