import requests
from config import OPENDENTAL_API_KEY, OPENDENTAL_BASE_URL

_TABLE_FIELDS = {
    "PatNum",
    "FName", "LName", "MiddleI", "Birthdate", "SSN",
    "HmPhone", "Address", "City", "State", "Zip",
    "Email", "priProvAbbr", "PatStatus", "BillingType",
}


def fetch_patient(fname: str, lname: str) -> list[dict]:
    resp = requests.get(
        f"{OPENDENTAL_BASE_URL}/patients/Simple",
        params={"FName": fname, "LName": lname},
        headers={"Authorization": f"ODFHIR {OPENDENTAL_API_KEY}"},
        timeout=15,
    )
    resp.raise_for_status()
    return [
        {k: v for k, v in record.items() if k in _TABLE_FIELDS}
        for record in resp.json()
    ]
