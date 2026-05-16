import random
import os
import uuid
from datetime import datetime, timedelta

from dotenv import load_dotenv
from faker import Faker
import psycopg2
from psycopg2.extras import execute_batch

# Load environment variables from .env file
load_dotenv()

# this creates faker object which generates:
# - fake ips
# - fake messages
# - fake usernames
fake = Faker()

# this connnects to the database
connection = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    database=os.getenv("DB_NAME", "log_management"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", ""),
    port=int(os.getenv("DB_PORT", 5432))
)

# create cursor which helps us to execute sql queries
cursor = connection.cursor()

# fetch IDs from services table
cursor.execute("SELECT service_id FROM services")
service_ids = [row[0] for row in cursor.fetchall()]

# fetch IDs from log_levels table
cursor.execute("SELECT log_level_id FROM log_levels")
log_level_ids = [row[0] for row in cursor.fetchall()]

# fetch IDs from error_categories table
cursor.execute("SELECT error_category_id FROM error_categories")
error_category_ids = [row[0] for row in cursor.fetchall()]

# fetch IDs from users table
cursor.execute("SELECT user_id FROM users")
user_ids = [row[0] for row in cursor.fetchall()]

# fetch IDs from api_endpoints table
cursor.execute("SELECT endpoint_id FROM api_endpoints")
endpoint_ids = [row[0] for row in cursor.fetchall()]

# fetch IDs from servers table
cursor.execute("SELECT server_id FROM servers")
server_ids = [row[0] for row in cursor.fetchall()]

batch_size = int(os.getenv("BATCH_SIZE", 5000))
total_logs = int(os.getenv("TOTAL_LOGS", 1000000))

# generate log data
def generate_log():
    return (
        str(uuid.uuid4()),
        random.choice(service_ids),
        random.choice(log_level_ids),
        random.choice(error_category_ids),
        random.choice(user_ids),
        random.choice(endpoint_ids),
        random.choice(server_ids),
        fake.sentence(),
        random.choice(["GET", "POST", "PUT", "DELETE"]),
        random.randint(50, 5000),
        fake.ipv4(),
        random.randint(200, 500),
        fake.date_time_between(
            start_date='-90d',
            end_date='now'
        )
    )

# insert query
insert_query = """
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

# generate many logs
logs = []
for i in range(0, total_logs, batch_size):
    current_batch_size = min(batch_size, total_logs - i)
    batch = [generate_log() for _ in range(current_batch_size)]
    execute_batch(cursor, insert_query, batch)
    connection.commit()
    print(f"Inserted {i + current_batch_size} logs")

# close connection
cursor.close()
connection.close()
