import json
from db.database import get_connection


def _mask_ssn(ssn: str) -> str:
    if not ssn:
        return ""
    digits = ssn.replace("-", "")
    if len(digits) >= 4:
        return f"***-**-{digits[-4:]}"
    return "***-**-****"


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
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO patients
               (PatNum,FName, LName, MiddleI, Birthdate, SSN, HmPhone, Address,
                City, State, Zip, Email, priProvAbbr, PatStatus, BillingType)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (int(pat_num) if pat_num != "" else None,
             fname, lname, middle_i, birthdate, ssn, hm_phone, address,
             city, state, zip_code, email, pri_prov_abbr, pat_status, billing_type),
        )
   
        # pat_num = cur.lastrowid
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
    finally:
        conn.close()
    return payload


def get_session_patients(ids: list[int], page: int = 1, page_size: int = 10):
    if not ids:
        return [], 0
    placeholders = ",".join("?" * len(ids))
    conn = get_connection()
    try:
        total = conn.execute(
            f"SELECT COUNT(*) FROM patients WHERE PatNum IN ({placeholders})", ids
        ).fetchone()[0]
        offset = (page - 1) * page_size
        rows = conn.execute(
            f"""SELECT PatNum, FName, LName, MiddleI, Birthdate, SSN,
                       HmPhone, Address, City, State, Zip, Email,
                       priProvAbbr, PatStatus, BillingType
                FROM patients WHERE PatNum IN ({placeholders})
                ORDER BY PatNum DESC LIMIT ? OFFSET ?""",
            ids + [page_size, offset],
        ).fetchall()
    finally:
        conn.close()
    records = []
    for r in rows:
        d = dict(r)
        d["SSN"] = _mask_ssn(d["SSN"])
        records.append(d)
    return records, total


def get_patients_by_ids(ids: list[int]) -> list[dict]:
    if not ids:
        return []
    placeholders = ",".join("?" * len(ids))
    conn = get_connection()
    try:
        rows = conn.execute(
            f"SELECT * FROM patients WHERE PatNum IN ({placeholders})", ids
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


def log_audit(action: str, record_id: int | None, payload_dict: dict):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO audit_logs (action, record_id, payload) VALUES (?, ?, ?)",
            (action, record_id, json.dumps(payload_dict)),
        )
        conn.commit()
    finally:
        conn.close()
