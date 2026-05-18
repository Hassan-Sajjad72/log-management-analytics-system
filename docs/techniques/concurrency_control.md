# Concurrency Control

## Overview

PostgreSQL uses **MVCC (Multi-Version Concurrency Control)** as its foundational concurrency mechanism. In MVCC:

- **readers never block writers** — a SELECT can see a consistent snapshot while INSERT/UPDATE/DELETE statements run
- **writers never block readers** — an INSERT or UPDATE creates a new row version without modifying the current visible version
- **no read locks** — traditional database systems use read locks to prevent dirty reads, but MVCC avoids them entirely by serving historical versions

This is critical for log-heavy systems where reads and writes happen simultaneously at high volume.

## Why It Matters for Logs

This project has a unique workload pattern:

- **High write volume**: services continuously insert log records (e.g., 1 million logs every day from `generate_logs.py`)
- **High read volume**: dashboards and analytics queries constantly scan logs for summaries and reports
- **Simultaneous access**: while one thread inserts, another may be aggregating the last 30 days of logs

Without MVCC (or proper concurrency control):

- reads would have to wait for write locks, causing dashboard latency spikes
- writes would stall while analytics queries held read locks
- partial queries could see torn or inconsistent data

With MVCC:

- insertions proceed at full speed without blocking analytics
- analytics queries see clean, consistent snapshots from when they started
- no artificial lock contention between readers and writers

## What Was Implemented

PostgreSQL's built-in MVCC is always enabled, but several concurrency control patterns were demonstrated for this project:

### 1. Isolation Levels

Two common isolation levels are supported:

- **READ COMMITTED** (PostgreSQL default): each SQL statement sees the latest committed data from its execution point
- **REPEATABLE READ**: the entire transaction sees a consistent snapshot from when it started (useful for multi-statement workflows)

Demo: [sql/concurrency/01_isolation_levels_demo.sql](../../sql/concurrency/01_isolation_levels_demo.sql)

### 2. Row-Level Locking

When you need to lock a specific row during an update:

- **SELECT FOR UPDATE**: acquires an exclusive lock on the selected row, preventing other transactions from updating or deleting it
- Useful for update-check-update patterns (for example, flagging or updating a specific log record)

Demo: [sql/concurrency/02_row_level_locking_demo.sql](../../sql/concurrency/02_row_level_locking_demo.sql)

### 3. Concurrent Inserts

Multiple services can insert logs simultaneously without conflict:

- each transaction creates its own row version
- commit is atomic per transaction
- no waiting for table-level locks

Demo: [sql/concurrency/03_concurrent_insert_simulation.sql](../../sql/concurrency/03_concurrent_insert_simulation.sql)

### 4. Deadlock Prevention

Consistent lock ordering avoids circular waits:

- always lock resources in the same order across transactions
- prevents deadlock where Transaction A waits for B and B waits for A

Demo: [sql/concurrency/04_deadlock_prevention_demo.sql](../../sql/concurrency/04_deadlock_prevention_demo.sql)

### 5. MVCC Visibility & VACUUM

Old row versions are retained until no active transaction can see them, then **VACUUM** cleans them up:

- MVCC requires more storage (multiple versions per row)
- VACUUM reclaims space by removing dead tuples
- autovacuum runs regularly to prevent table bloat

Demo: [sql/concurrency/05_mvcc_visibility_demo.sql](../../sql/concurrency/05_mvcc_visibility_demo.sql)

### 6. Lock Monitoring

Monitor active locks and blocking sessions during concurrent workloads:

- check active transactions with `pg_stat_activity`
- identify which transaction is blocking which
- useful for troubleshooting performance during high concurrency

Monitoring queries: [sql/benchmarks/concurrency/01_lock_monitoring.sql](../../sql/benchmarks/concurrency/01_lock_monitoring.sql)

## The CONCURRENTLY Connection

**REFRESH MATERIALIZED VIEW CONCURRENTLY** is itself a concurrency control feature:

- `REFRESH MATERIALIZED VIEW` (without CONCURRENTLY) locks the view and blocks all reads during refresh
- `REFRESH MATERIALIZED VIEW CONCURRENTLY` computes a new result set in the background, then atomically swaps it
- reads can continue during the refresh because MVCC serves the old snapshot until the new one is ready

This is visible in [sql/schema/02_refresh_materialized_views.sql](../../sql/schema/02_refresh_materialized_views.sql), where refreshes use CONCURRENTLY to avoid locking dashboards during the update.

## How It Works

MVCC maintains multiple versions of each row:

1. When a transaction starts, PostgreSQL assigns it a transaction ID (XID)
2. The transaction sees rows inserted before its XID started
3. Rows inserted after the transaction started are invisible to that transaction (even if committed)
4. When the transaction commits, its changes become visible to new transactions
5. Old row versions stay in the table until VACUUM can confirm no active transaction needs them

Example scenario:

- Transaction A starts, queries 1,000,000 logs
- Transaction B inserts 100,000 new logs, commits
- Transaction A's query still sees exactly 1,000,000 logs (snapshot isolation)
- After Transaction A commits, new transactions see 1,100,000 logs

## Performance Impact

Concurrency control has measurable trade-offs:

| Aspect | Benefit | Cost |
| --- | --- | --- |
| MVCC | readers never block writers | requires storage for multiple row versions |
| REPEATABLE READ isolation | strong consistency for multi-statement transactions | more lock conflict potential |
| READ COMMITTED isolation | lower lock contention | weaker consistency (sees uncommitted changes) |
| Row-level locking (SELECT FOR UPDATE) | fine-grained control during updates | adds lock overhead per row |
| VACUUM | reclaims dead-tuple space | consumes CPU/I/O during maintenance |

## Benefits

- no reader-writer blocking, allowing dashboards and inserts to coexist
- strong snapshot isolation for consistent analytics queries
- atomic writes: either the entire transaction commits or none of it
- dead tuple cleanup prevents unbounded table growth
- lock monitoring tools for diagnosing contention

## Trade-Offs

- **higher isolation = more lock contention**: REPEATABLE READ must hold more locks than READ COMMITTED
- **MVCC storage overhead**: every update creates a new row version, using more disk space until VACUUM
- **VACUUM maintenance**: autovacuum runs regularly and consumes CPU and I/O
- **transaction ID wraparound**: very long-running transactions can prevent VACUUM, potentially causing problems
- **complexity**: understanding MVCC and isolation levels requires familiarity with PostgreSQL concepts

## Best Use In This Project

Concurrency control is best for:

- simultaneous log inserts from multiple services
- real-time dashboard queries while logs are being written
- materialized view refreshes that don't block analytics (CONCURRENTLY)
- applications that need strong consistency (REPEATABLE READ for multi-statement workflows)

Concurrency control is less critical for:

- single-threaded or low-concurrency systems
- batch-only workloads that don't mix reads and writes
- write-only scenarios (logs that are never updated)

## Conclusion

MVCC is PostgreSQL's primary answer to the reader-writer concurrency problem: queries can run in parallel without lock contention. For this log-management system, MVCC enables the simultaneous high-volume inserts and analytics workloads that are core to the use case.

By understanding isolation levels, row-level locking, and VACUUM maintenance, you can tune concurrency control to match the project's needs: strong consistency where required, minimal lock contention for the write-heavy ingestion path, and efficient refresh of materialized views via CONCURRENTLY.
