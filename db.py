# db.py
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "dbname": "movietheater",
    "user": "movietheater_user",
    "password": "DpqonU3tkphMU0Y160g3VZpXyDZOoyff",
    "host": "d1m7efm3jp1c73edteo0-a.singapore-postgres.render.com",
    "port": 5432
}

def get_connection():
    return psycopg2.connect(cursor_factory=RealDictCursor, **DB_CONFIG)

def fetchall(query, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
    finally:
        conn.close()

def fetchone(query, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()
    finally:
        conn.close()
