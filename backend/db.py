# create DB connection

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from flask import session, has_request_context

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

def apply_rls_context(cursor):
    cursor.execute("SET ROLE web_user;")
    if has_request_context():
        team = session.get('team', '')
        cursor.execute("SET app.current_team = %s;", (team,))
    else:
        cursor.execute("SET app.current_team = 'Admin';")

def fetch_all(query, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            apply_rls_context(cursor)
            if params is not None:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    finally:
        conn.close()

def fetch_one(query, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            apply_rls_context(cursor)
            if params is not None:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
    finally:
        conn.close()

def execute_command(query):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            apply_rls_context(cursor)
            cursor.execute(query)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
