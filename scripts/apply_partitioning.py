import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "log_management"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        port=int(os.getenv("DB_PORT", 5432))
    )

def run_sql_file(cursor, filepath):
    print(f"Executing SQL file: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        sql = f.read()
    # Execute the entire script
    cursor.execute(sql)

def main():
    conn = get_connection()
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            # 1. Drop materialized views first to avoid dependency blocks
            print("Dropping materialized views...")
            cur.execute("DROP MATERIALIZED VIEW IF EXISTS mv_log_olap_daily;")
            cur.execute("DROP MATERIALIZED VIEW IF EXISTS mv_daily_service_activity;")
            cur.execute("DROP MATERIALIZED VIEW IF EXISTS mv_daily_endpoint_latency;")
            cur.execute("DROP MATERIALIZED VIEW IF EXISTS mv_daily_status_code_distribution;")

            # Check if logs_unpartitioned already exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'logs_unpartitioned'
                );
            """)
            unpart_exists = cur.fetchone()[0]

            # Check if logs is already partitioned
            cur.execute("""
                SELECT relkind FROM pg_class 
                WHERE relname = 'logs' AND relnamespace = 'public'::regnamespace;
            """)
            res = cur.fetchone()
            is_partitioned = res and res[0] == 'p'

            if is_partitioned:
                print("Table 'logs' is already partitioned.")
                if not unpart_exists:
                    print("Error: logs is partitioned, but logs_unpartitioned does not exist.")
                    # We might want to create logs_unpartitioned from logs, but let's see.
            else:
                if unpart_exists:
                    print("Table 'logs_unpartitioned' already exists. Dropping it first for a clean partition run.")
                    cur.execute("DROP TABLE IF EXISTS logs_unpartitioned CASCADE;")
                
                # 2. Run the partitioning script
                run_sql_file(cur, "sql/schema/05_create_partitioned_logs.sql")

            # 3. Create indexes on the partitioned logs table
            run_sql_file(cur, "sql/schema/04_create_indexes.sql")

            # 4. Create corresponding indexes on logs_unpartitioned for a fair benchmark comparison
            print("Creating indexes on logs_unpartitioned...")
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_unpart_created_at
                    ON logs_unpartitioned (created_at DESC);
                
                CREATE INDEX IF NOT EXISTS idx_unpart_log_level_id
                    ON logs_unpartitioned (log_level_id);
                
                CREATE INDEX IF NOT EXISTS idx_unpart_service_created_at
                    ON logs_unpartitioned (service_id, created_at DESC);
                
                CREATE INDEX IF NOT EXISTS idx_unpart_service_log_level
                    ON logs_unpartitioned (service_id, log_level_id);
                
                CREATE INDEX IF NOT EXISTS idx_unpart_errors_only
                    ON logs_unpartitioned (service_id, created_at DESC)
                    WHERE log_level_id IN (4, 5);
            """)

            # 5. Recreate materialized views (they will now reference the partitioned logs table)
            run_sql_file(cur, "sql/schema/01_create_materialized_views.sql")
            run_sql_file(cur, "sql/schema/03_create_olap_aggregation.sql")
            
            # 6. Refresh the materialized views to populate them with data
            run_sql_file(cur, "sql/schema/02_refresh_materialized_views.sql")

            conn.commit()
            print("Successfully partitioned the logs table, migrated all data, created indexes, and recreated materialized views!")
    except Exception as e:
        conn.rollback()
        print(f"Error during partitioning: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
