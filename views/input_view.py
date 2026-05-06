import streamlit as st
from api_client import fetch_patient
from db.crud import create_patient


def render():
    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="padding: 1.5rem 0 0.5rem 0;">
            <h1 style="margin: 0; font-size: 2rem; font-weight: 700; letter-spacing: -0.5px;">
                Docudent Ingestion Interface
            </h1>
            <p style="margin: 0.25rem 0 0 0; color: grey; font-size: 0.95rem;">
                Look up a patient via the OpenDental API and save their record for ingestion.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Form ─────────────────────────────────────────────────────────────────
    st.markdown("##### Patient Lookup")
    st.caption("First Name and Last Name are required. SSN is optional.")

    with st.form("lookup_form", clear_on_submit=False):
        col1, col2, col3 = st.columns([3, 3, 2])
        fname = col1.text_input("First Name *")
        lname = col2.text_input("Last Name *")
        ssn   = col3.text_input("SSN", placeholder="XXX-XX-XXXX")
        submitted = st.form_submit_button("Look Up Patient", type="primary", use_container_width=True)

    # ── Lookup & save ─────────────────────────────────────────────────────────
    if submitted:
        errors = []
        if not fname.strip():
            errors.append("First Name is required.")
        if not lname.strip():
            errors.append("Last Name is required.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            with st.spinner("Fetching from OpenDental API…"):
                try:
                    results = fetch_patient(fname.strip(), lname.strip())
                except Exception as e:
                    st.error(f"API error: {e}")
                    results = None

            if results is None:
                pass  # error already shown
            elif len(results) == 0:
                st.warning(f"No patient found for **{fname.strip()} {lname.strip()}**.")
            else:
                # Use first match; merge user-supplied SSN if API returned none
                patient_data = results[0]
                if not patient_data.get("SSN") and ssn.strip():
                    patient_data["SSN"] = ssn.strip()

                record = create_patient(
                    pat_num      = patient_data.get("PatNum",""),  
                    fname        = patient_data.get("FName", fname.strip()),
                    lname        = patient_data.get("LName", lname.strip()),
                    ssn          = patient_data.get("SSN", ssn.strip()),
                    middle_i     = patient_data.get("MiddleI", ""),
                    birthdate    = patient_data.get("Birthdate", ""),
                    hm_phone     = patient_data.get("HmPhone", ""),
                    address      = patient_data.get("Address", ""),
                    city         = patient_data.get("City", ""),
                    state        = patient_data.get("State", ""),
                    zip_code     = patient_data.get("Zip", ""),
                    email        = patient_data.get("Email", ""),
                    pri_prov_abbr= patient_data.get("priProvAbbr", ""),
                    pat_status   = patient_data.get("PatStatus", "Patient"),
                    billing_type = patient_data.get("BillingType", "Standard Account"),
                )

                if "session_pat_nums" not in st.session_state:
                    st.session_state.session_pat_nums = []
                st.session_state.session_pat_nums.append(record["PatNum"])

                st.success(
                    f"Saved — **{record['FName']} {record['LName']}** "
                    f"(Patient ID: {record['PatNum']})"
                )

                # Show what was pulled from the API
                with st.expander("Record saved to database", expanded=False):
                    st.json(patient_data)

                if len(results) > 1:
                    st.info(
                        f"{len(results)} matches found — saved the first result. "
                        "Refine the name if a different patient was intended."
                    )

    # ── Navigation ────────────────────────────────────────────────────────────
    st.markdown("---")
    ncol1, ncol2 = st.columns([3, 1])
    with ncol2:
        if st.button("View Export →", type="secondary", use_container_width=True):
            st.session_state.page = "export"
            st.rerun()
