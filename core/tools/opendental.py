import httpx
from config import OPENDENTAL_API_KEY, OPENDENTAL_BASE_URL
from db.models import PATIENT_FIELDS, FIELD_MAP
from utils import logger

log = logger.get("tools.opendental")


def _normalize_record(record: dict, patient_ref: str) -> dict:
    normalized: dict = {}

    for api_key, value in record.items():
        canonical = FIELD_MAP.get(api_key.lower())
        if canonical:
            normalized[canonical] = value

    missing = [f for f in PATIENT_FIELDS if f not in normalized]
    if missing:
        log.warning("Fields missing from API response for %s: %s", patient_ref, missing)

    for field in missing:
        normalized[field] = ""

    return normalized


async def fetch_patient(fname: str, lname: str) -> list[dict]:
    patient_ref = f"{fname} {lname}"
    log.info("Fetching patient from OpenDental API: %s", patient_ref)

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{OPENDENTAL_BASE_URL}/patients/Simple",
                params={"FName": fname, "LName": lname},
                headers={"Authorization": f"ODFHIR {OPENDENTAL_API_KEY}"},
            )
            resp.raise_for_status()
    except httpx.TimeoutException:
        log.error("API request timed out for %s", patient_ref)
        raise
    except httpx.HTTPStatusError as e:
        log.error("API HTTP error for %s: %s %s", patient_ref, e.response.status_code, e.response.text)
        raise
    except httpx.RequestError as e:
        log.error("API request failed for %s: %s", patient_ref, e)
        raise

    raw = resp.json()
    log.debug("API returned %d record(s) for %s", len(raw), patient_ref)

    results = [_normalize_record(record, patient_ref) for record in raw]

    if not results:
        log.warning("No records found for %s", patient_ref)
    else:
        log.info("Fetched and normalized %d record(s) for %s", len(results), patient_ref)

    return results
