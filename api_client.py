import requests

_BASE_URL = "https://api.opendental.com/api/v1"
_HEADERS = {"Authorization": "ODFHIR NFF6i0KrXrxDkZHt/VzkmZEaUWOjnQX2z"}

# Columns that exist in the patients table — used to filter API response
_TABLE_FIELDS = {
    "PatNum",
    "FName", "LName", "MiddleI", "Birthdate", "SSN",
    "HmPhone", "Address", "City", "State", "Zip",
    "Email", "priProvAbbr", "PatStatus", "BillingType",
}


def fetch_patient(fname: str, lname: str) -> list[dict]:
    """
    Query the OpenDental Simple patients endpoint.
    Returns a list of records filtered to only patients-table columns.
    Raises on HTTP errors.
    """
    resp = requests.get(
        f"{_BASE_URL}/patients/Simple",
        params={"FName": fname, "LName": lname},
        headers=_HEADERS,
        timeout=15,
    )
    resp.raise_for_status()
    results = resp.json()
    return [
        {k: v for k, v in record.items() if k in _TABLE_FIELDS}
        for record in results
    ]
