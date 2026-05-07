PATIENT_FIELDS = {
    "PatNum", "FName", "LName", "MiddleI", "Birthdate", "SSN",
    "HmPhone", "Address", "City", "State", "Zip",
    "Email", "priProvAbbr", "PatStatus", "BillingType",
}

# Case-insensitive lookup: lowercase -> canonical field name
FIELD_MAP = {f.lower(): f for f in PATIENT_FIELDS}

# Default values for missing fields
DEFAULTS = {f: "" for f in PATIENT_FIELDS}
