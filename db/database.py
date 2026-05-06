import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docudent.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS patients (
                PatNum      INTEGER PRIMARY KEY AUTOINCREMENT,
                FName       TEXT,
                LName       TEXT,
                MiddleI     TEXT,
                Birthdate   TEXT,
                SSN         TEXT,
                HmPhone     TEXT,
                Address     TEXT,
                City        TEXT,
                State       TEXT,
                Zip         TEXT,
                Email       TEXT,
                priProvAbbr TEXT,
                PatStatus   TEXT DEFAULT 'Patient',
                BillingType TEXT DEFAULT 'Standard Account'
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                action    TEXT NOT NULL,
                record_id INTEGER,
                payload   TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
    finally:
        conn.close()
