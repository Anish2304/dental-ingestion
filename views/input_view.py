import streamlit as st
from services.api_client import fetch_patient
from db.crud import create_patient, check_patient_exists


def _do_lookup(i: int):
    fname = st.session_state.get(f"fname_{i}", "").strip()
    lname = st.session_state.get(f"lname_{i}", "").strip()
    ssn   = st.session_state.get(f"ssn_{i}",   "").strip()

    if not fname or not lname:
        st.session_state.lookup_rows[i]["status"]  = "error"
        st.session_state.lookup_rows[i]["message"] = "First and Last Name are required."
        return

    existing = check_patient_exists(fname, lname)
    if existing:
        dob   = existing.get("Birthdate") or "—"
        phone = existing.get("HmPhone")   or "—"
        st.session_state.lookup_rows[i]["status"]  = "exists"
        st.session_state.lookup_rows[i]["message"] = (
            f"Patient **{existing['FName']} {existing['LName']}** already exists in the database "
            f"(ID: {existing['PatNum']}, DOB: {dob}, Phone: {phone})."
        )
        return

    try:
        results = fetch_patient(fname, lname)
    except Exception as e:
        st.session_state.lookup_rows[i]["status"]  = "error"
        st.session_state.lookup_rows[i]["message"] = f"API error: {e}"
        return

    if not results:
        st.session_state.lookup_rows[i]["status"]  = "not_found"
        st.session_state.lookup_rows[i]["message"] = f"No patient found for {fname} {lname}."
        return

    patient_data = results[0]
    if not patient_data.get("SSN") and ssn:
        patient_data["SSN"] = ssn

    record = create_patient(
        pat_num       = patient_data.get("PatNum", ""),
        fname         = patient_data.get("FName", fname),
        lname         = patient_data.get("LName", lname),
        ssn           = patient_data.get("SSN", ssn),
        middle_i      = patient_data.get("MiddleI", ""),
        birthdate     = patient_data.get("Birthdate", ""),
        hm_phone      = patient_data.get("HmPhone", ""),
        address       = patient_data.get("Address", ""),
        city          = patient_data.get("City", ""),
        state         = patient_data.get("State", ""),
        zip_code      = patient_data.get("Zip", ""),
        email         = patient_data.get("Email", ""),
        pri_prov_abbr = patient_data.get("priProvAbbr", ""),
        pat_status    = patient_data.get("PatStatus", "Patient"),
        billing_type  = patient_data.get("BillingType", "Standard Account"),
    )

    st.session_state.lookup_rows[i]["status"]  = "saved"
    st.session_state.lookup_rows[i]["message"] = (
        f"Saved — **{record['FName']} {record['LName']}** (Patient ID: {record['PatNum']})"
    )


def render():
    st.markdown(
        """
        <div style="padding: 1.5rem 0 0.5rem 0;">
            <h1 style="margin: 0; font-size: 2rem; font-weight: 700; letter-spacing: -0.5px;">
                Docudent Ingestion Interface
            </h1>
            <p style="margin: 0.25rem 0 0 0; color: grey; font-size: 0.95rem;">
                Look up patients via the OpenDental API and save their records for ingestion. Existing patients will be flagged automatically.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    if "lookup_rows" not in st.session_state:
        st.session_state.lookup_rows = [{"status": None, "message": ""}]

    # Column headers
    h1, h2, h3, h4 = st.columns([3, 3, 2, 1.2])
    h1.markdown("**First Name** *")
    h2.markdown("**Last Name** *")
    h3.markdown("**SSN**")

    for i, row in enumerate(st.session_state.lookup_rows):
        c1, c2, c3, c4 = st.columns([3, 3, 2, 1.2])
        c1.text_input("First Name", key=f"fname_{i}", label_visibility="collapsed", placeholder="John")
        c2.text_input("Last Name",  key=f"lname_{i}", label_visibility="collapsed", placeholder="Doe")
        c3.text_input("SSN",        key=f"ssn_{i}",   label_visibility="collapsed", placeholder="XXX-XX-XXXX")

        if c4.button("Look Up", key=f"lookup_{i}", use_container_width=True):
            _do_lookup(i)

        if row["status"] == "saved":
            st.success(row["message"])
        elif row["status"] == "exists":
            st.warning(row["message"])
        elif row["status"] == "error":
            st.error(row["message"])
        elif row["status"] == "not_found":
            st.warning(row["message"])

    st.markdown("")
    if st.button("+ Add Patient"):
        st.session_state.lookup_rows.append({"status": None, "message": ""})
        st.rerun()

    # ── Navigation ────────────────────────────────────────────────────────────
    st.markdown("---")
    ncol1, ncol2 = st.columns([3, 1])
    with ncol2:
        if st.button("View Export →", type="secondary", use_container_width=True):
            st.session_state.page = "export"
            st.rerun()
