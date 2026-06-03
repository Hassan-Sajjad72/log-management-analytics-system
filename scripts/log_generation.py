import os
import random
import uuid
from datetime import datetime, timezone

import psycopg2
from dotenv import load_dotenv
from faker import Faker
from psycopg2.extras import execute_batch

load_dotenv()

fake = Faker()

INSERT_LOG_QUERY = """
INSERT INTO logs (
    request_id,
    service_id,
    log_level_id,
    error_category_id,
    user_id,
    endpoint_id,
    server_id,
    message,
    method,
    response_time_ms,
    ip_address,
    status_code,
    created_at
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "log_management"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        port=int(os.getenv("DB_PORT", 5432))
    )

def load_reference_ids(cursor):
    tables = {
        "service_ids": "SELECT service_id FROM services",
        "log_level_ids": "SELECT log_level_id FROM log_levels",
        "error_category_ids": "SELECT error_category_id FROM error_categories",
        "user_ids": "SELECT user_id FROM users",
        "endpoint_ids": "SELECT endpoint_id FROM api_endpoints",
        "server_ids": "SELECT server_id FROM servers",
    }

    reference_ids = {}
    for key, query in tables.items():
        cursor.execute(query)
        ids = [row[0] for row in cursor.fetchall()]
        if not ids:
            raise RuntimeError(f"No rows found for {key}. Run the seed scripts first.")
        reference_ids[key] = ids

    return reference_ids

def generate_log(reference_ids, live=False):
    created_at = datetime.now(timezone.utc) if live else fake.date_time_between(
        start_date='-867d',
        end_date='now'
    )

    return (
        str(uuid.uuid4()),
        random.choice(reference_ids["service_ids"]),
        random.choice(reference_ids["log_level_ids"]),
        random.choice(reference_ids["error_category_ids"]),
        random.choice(reference_ids["user_ids"]),
        random.choice(reference_ids["endpoint_ids"]),
        random.choice(reference_ids["server_ids"]),
        fake.sentence(),
        random.choice(["GET", "POST", "PUT", "DELETE"]),
        random.randint(50, 5000),
        fake.ipv4(),
        random.randint(200, 500),
        created_at
    )

def insert_log_batch(cursor, reference_ids, batch_size, live=False):
    batch = [generate_log(reference_ids, live=live) for _ in range(batch_size)]
    execute_batch(cursor, INSERT_LOG_QUERY, batch)
    return len(batch)
