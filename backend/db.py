# create DB connection

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
        cursor_factory=RealDictCursor
    )

def fetch_all(query, params=None):

    # call DB connection method
    conn = get_connection()
    cursor = conn.cursor()

    # execute query
    cursor.execute(query, params or ())
    rows = cursor.fetchall()

    # after executing query -> close DB connection
    cursor.close()
    conn.close()

    return rows

def fetch_one(query, params=None):
    # call DB connection method
    conn = get_connection()
    cursor = conn.cursor()

    # execute query
    cursor.execute(query, params or ())
    row = cursor.fetchone()

    # after executing query -> close DB connection
    cursor.close()
    conn.close()

    return row
