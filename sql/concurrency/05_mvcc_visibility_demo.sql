-- Demonstrates MVCC (Multi-Version Concurrency Control).
-- PostgreSQL never overwrites data in place — it creates new row versions.
-- Old versions are cleaned up by VACUUM.

-- Check current transaction ID (each transaction gets a unique XID)
SELECT txid_current();

-- Check dead tuples (old row versions not yet vacuumed)
SELECT
    relname AS table_name,
    n_live_tup AS live_rows,
    n_dead_tup AS dead_rows,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE relname = 'logs';

-- Manually trigger vacuum to clean dead tuples
VACUUM ANALYZE logs;

-- Re-check after vacuum
SELECT
    relname,
    n_live_tup,
    n_dead_tup
FROM pg_stat_user_tables
WHERE relname = 'logs';