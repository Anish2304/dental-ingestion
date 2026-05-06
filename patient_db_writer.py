import sqlite3
import os

PATIENT_DB_PATH = os.path.join(os.path.dirname(__file__), "patients.db")


def _get_connection():
    conn = sqlite3.connect(PATIENT_DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _init_patient_db(conn: sqlite3.Connection):
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
    """)


def write_ingested_patients(records: list[dict]) -> int:
    """
    Write a list of patient dicts (from the ingest JSON) into patient.db.
    Creates the DB and table if they don't exist.
    Returns the number of rows inserted.
    """
    conn = _get_connection()
    try:
        _init_patient_db(conn)
        cur = conn.cursor()
        inserted = 0
        for r in records:
            cur.execute(
                """INSERT INTO patients
                   (FName, LName, MiddleI, Birthdate, SSN, HmPhone, Address,
                    City, State, Zip, Email, priProvAbbr, PatStatus, BillingType)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    r.get("FName", ""),
                    r.get("LName", ""),
                    r.get("MiddleI", ""),
                    r.get("Birthdate", ""),
                    r.get("SSN", ""),
                    r.get("HmPhone", ""),
                    r.get("Address", ""),
                    r.get("City", ""),
                    r.get("State", ""),
                    r.get("Zip", ""),
                    r.get("Email", ""),
                    r.get("priProvAbbr", ""),
                    r.get("PatStatus", "Patient"),
                    r.get("BillingType", "Standard Account"),
                ),
            )
            inserted += 1
        conn.commit()
    finally:
        conn.close()
    return inserted
