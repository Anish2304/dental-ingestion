import json
from db.database import get_connection
from utils import logger

log = logger.get("db.crud")


def _mask_ssn(ssn: str) -> str:
    if not ssn:
        return ""
    digits = ssn.replace("-", "")
    if len(digits) >= 4:
        return f"***-**-{digits[-4:]}"
    return "***-**-****"


def check_patient_exists(fname: str, lname: str) -> dict | None:
    log.debug("Checking duplicate for: %s %s", fname, lname)
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT PatNum, FName, LName, Birthdate, HmPhone FROM patients "
            "WHERE LOWER(FName)=LOWER(?) AND LOWER(LName)=LOWER(?) LIMIT 1",
            (fname, lname),
        ).fetchone()
    except Exception as e:
        log.error("check_patient_exists failed for %s %s: %s", fname, lname, e, exc_info=True)
        raise
    finally:
        conn.close()
    if row:
        log.info("Duplicate found for %s %s (PatNum=%s)", fname, lname, row["PatNum"])
    return dict(row) if row else None


def create_patient(
    pat_num: int,
    fname: str,
    lname: str,
    ssn: str = "",
    middle_i: str = "",
    birthdate: str = "",
    hm_phone: str = "",
    address: str = "",
    city: str = "",
    state: str = "",
    zip_code: str = "",
    email: str = "",
    pri_prov_abbr: str = "",
    pat_status: str = "Patient",
    billing_type: str = "Standard Account",
) -> dict:
    log.info("Creating patient: %s %s (PatNum=%s)", fname, lname, pat_num)
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO patients
               (PatNum, FName, LName, MiddleI, Birthdate, SSN, HmPhone, Address,
                City, State, Zip, Email, priProvAbbr, PatStatus, BillingType)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (int(pat_num) if pat_num != "" else None,
             fname, lname, middle_i, birthdate, ssn, hm_phone, address,
             city, state, zip_code, email, pri_prov_abbr, pat_status, billing_type),
        )
        payload = {
            "PatNum": pat_num, "FName": fname, "LName": lname, "MiddleI": middle_i,
            "Birthdate": birthdate, "SSN": ssn, "HmPhone": hm_phone, "Address": address,
            "City": city, "State": state, "Zip": zip_code, "Email": email,
            "priProvAbbr": pri_prov_abbr, "PatStatus": pat_status, "BillingType": billing_type,
        }
        cur.execute(
            "INSERT INTO audit_logs (action, record_id, payload) VALUES (?, ?, ?)",
            ("INSERT", pat_num, json.dumps(payload)),
        )
        conn.commit()
        log.info("Patient saved to DB: %s %s (PatNum=%s)", fname, lname, pat_num)
    except Exception as e:
        conn.rollback()
        log.error("create_patient failed for %s %s: %s", fname, lname, e, exc_info=True)
        raise
    finally:
        conn.close()
    return payload


def get_all_patients(page: int = 1, page_size: int = 10):
    log.debug("get_all_patients called: page=%d page_size=%d", page, page_size)
    conn = get_connection()
    try:
        total = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
        offset = (page - 1) * page_size
        rows = conn.execute(
            """SELECT PatNum, FName, LName, MiddleI, Birthdate, SSN,
                      HmPhone, Address, City, State, Zip, Email,
                      priProvAbbr, PatStatus, BillingType
               FROM patients ORDER BY rowid DESC LIMIT ? OFFSET ?""",
            [page_size, offset],
        ).fetchall()
    except Exception as e:
        log.error("get_all_patients failed: %s", e, exc_info=True)
        raise
    finally:
        conn.close()
    records = []
    for r in rows:
        d = dict(r)
        d["SSN"] = _mask_ssn(d["SSN"])
        records.append(d)
    log.debug("get_all_patients returned %d record(s) (total=%d)", len(records), total)
    return records, total


def get_patients_by_ids(ids: list[int]) -> list[dict]:
    if not ids:
        return []
    log.debug("get_patients_by_ids: %s", ids)
    placeholders = ",".join("?" * len(ids))
    conn = get_connection()
    try:
        rows = conn.execute(
            f"SELECT * FROM patients WHERE PatNum IN ({placeholders})", ids
        ).fetchall()
    except Exception as e:
        log.error("get_patients_by_ids failed: %s", e, exc_info=True)
        raise
    finally:
        conn.close()
    return [dict(r) for r in rows]


def get_all_patients_full() -> list[dict]:
    log.debug("get_all_patients_full called")
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM patients ORDER BY rowid DESC").fetchall()
    except Exception as e:
        log.error("get_all_patients_full failed: %s", e, exc_info=True)
        raise
    finally:
        conn.close()
    log.debug("get_all_patients_full returned %d record(s)", len(rows))
    return [dict(r) for r in rows]


def delete_patients_by_ids(ids: list[int]):
    if not ids:
        return
    log.info("Deleting patients from DB: %s", ids)
    placeholders = ",".join("?" * len(ids))
    conn = get_connection()
    try:
        conn.execute(f"DELETE FROM patients WHERE PatNum IN ({placeholders})", ids)
        conn.commit()
        log.info("Deleted %d patient(s) from DB", len(ids))
    except Exception as e:
        conn.rollback()
        log.error("delete_patients_by_ids failed for ids=%s: %s", ids, e, exc_info=True)
        raise
    finally:
        conn.close()


def log_audit(action: str, record_id: int | None, payload_dict: dict):
    log.debug("Audit log: action=%s record_id=%s", action, record_id)
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO audit_logs (action, record_id, payload) VALUES (?, ?, ?)",
            (action, record_id, json.dumps(payload_dict)),
        )
        conn.commit()
    except Exception as e:
        log.error("log_audit failed: action=%s record_id=%s: %s", action, record_id, e, exc_info=True)
        raise
    finally:
        conn.close()
