import os
from log_generation import get_connection, insert_log_batch, load_reference_ids

batch_size = int(os.getenv("BATCH_SIZE", 5000))
total_logs = int(os.getenv("TOTAL_LOGS", 1000000))

connection = get_connection()
try:
    cursor = connection.cursor()
    reference_ids = load_reference_ids(cursor)

    for i in range(0, total_logs, batch_size):
        current_batch_size = min(batch_size, total_logs - i)
        insert_log_batch(cursor, reference_ids, current_batch_size)
        connection.commit()
        print(f"Inserted {i + current_batch_size} logs")
finally:
    cursor.close()
    connection.close()
