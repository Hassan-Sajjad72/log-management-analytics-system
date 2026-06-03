import os
import time

from log_generation import get_connection, insert_log_batch, load_reference_ids

LIVE_BATCH_SIZE = int(os.getenv("LIVE_BATCH_SIZE", 50))
LIVE_INTERVAL_SECONDS = float(os.getenv("LIVE_INTERVAL_SECONDS", 2))
LIVE_MAX_BATCHES = int(os.getenv("LIVE_MAX_BATCHES", 0))

def main():
    connection = get_connection()
    cursor = connection.cursor()
    total_inserted = 0
    batches_inserted = 0

    try:
        reference_ids = load_reference_ids(cursor)
        print(
            "Live log simulation started. "
            f"Inserting {LIVE_BATCH_SIZE} logs every {LIVE_INTERVAL_SECONDS} seconds."
        )
        print("Press Ctrl+C to stop.")

        while True:
            inserted = insert_log_batch(
                cursor,
                reference_ids,
                LIVE_BATCH_SIZE,
                live=True
            )
            connection.commit()
            total_inserted += inserted
            batches_inserted += 1
            print(f"Inserted {inserted} live logs. Total inserted: {total_inserted}")

            if LIVE_MAX_BATCHES and batches_inserted >= LIVE_MAX_BATCHES:
                print("Reached LIVE_MAX_BATCHES. Stopping simulation.")
                break

            time.sleep(LIVE_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nLive log simulation stopped.")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()
