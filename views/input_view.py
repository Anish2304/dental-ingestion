import streamlit as st
from core.agents import supervisor
from db.crud import create_patient, check_patient_exists



def _save_patient(i: int, patient_data: dict, ssn: str):
    if not patient_data.get("SSN") and ssn:
        patient_data["SSN"] = ssn

    record = create_patient(
        pat_num       = patient_data.get("PatNum", ""),
        fname         = patient_data.get("FName", ""),
        lname         = patient_data.get("LName", ""),
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

    if "session_pat_nums" not in st.session_state:
        st.session_state.session_pat_nums = []
    st.session_state.session_pat_nums.append(record["PatNum"])

    st.session_state.lookup_rows[i]["status"]     = "saved"
    st.session_state.lookup_rows[i]["message"]    = (
        f"Saved — **{record['FName']} {record['LName']}** (Patient ID: {record['PatNum']})"
    )
    st.session_state.lookup_rows[i]["candidates"] = []


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
            f"Patient **{existing['FName']} {existing['LName']}** already exists "
            f"(ID: {existing['PatNum']}, DOB: {dob}, Phone: {phone})."
        )
        return

    result = supervisor.lookup(fname, lname, ssn)
    if result["status"] == "error":
        st.session_state.lookup_rows[i]["status"]  = "not_found" if "No patient" in result["message"] else "error"
        st.session_state.lookup_rows[i]["message"] = result["message"]
        return

    data = result["data"]

    if result.get("multiple"):
        st.session_state.lookup_rows[i]["status"]     = "multiple"
        st.session_state.lookup_rows[i]["candidates"] = data
        st.session_state.lookup_rows[i]["ssn"]        = ssn
        st.session_state.lookup_rows[i]["message"]    = f"{len(data)} patients found — select the correct one."
        return

    _save_patient(i, data[0], ssn)


def render():
    # ── Header — matches HTML .page-title ──────────────────────────────────────
    st.markdown(
        """
        <div style="margin-bottom:20px;">
            <h1 style="font-size:21px;font-weight:700;color:#111827;
                       margin:0 0 5px;font-family:'DM Sans',sans-serif;">
                Patient Import
            </h1>
            <p style="font-size:13px;color:#6b7280;margin:0;
                      font-family:'DM Sans',sans-serif;">
                Look up patients via the OpenDental API and save their records for ingestion.
                Existing patients will be flagged automatically.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Section label ───────────────────────────────────────────────────────────
    st.markdown(
        "<p style='font-size:12px;font-weight:600;color:#6b7280;"
        "text-transform:uppercase;letter-spacing:0.07em;margin-bottom:4px;"
        "font-family:\"DM Sans\",sans-serif;'>Patient Lookup</p>",
        unsafe_allow_html=True,
    )
    st.caption("First Name and Last Name are required. SSN is optional.")

    if "lookup_rows" not in st.session_state:
        st.session_state.lookup_rows = [{"status": None, "message": ""}]

    # ── Column headers ──────────────────────────────────────────────────────────
    h1, h2, h3, _ = st.columns([3, 3, 2, 1.2])
    h1.markdown(
        "<p style='font-size:11.5px;font-weight:600;color:#6b7280;"
        "font-family:\"DM Sans\",sans-serif;margin:0;'>First Name *</p>",
        unsafe_allow_html=True,
    )
    h2.markdown(
        "<p style='font-size:11.5px;font-weight:600;color:#6b7280;"
        "font-family:\"DM Sans\",sans-serif;margin:0;'>Last Name *</p>",
        unsafe_allow_html=True,
    )
    h3.markdown(
        "<p style='font-size:11.5px;font-weight:600;color:#6b7280;"
        "font-family:\"DM Sans\",sans-serif;margin:0;'>SSN</p>",
        unsafe_allow_html=True,
    )

    # ── Rows ────────────────────────────────────────────────────────────────────
    for i, row in enumerate(st.session_state.lookup_rows):
        c1, c2, c3, c4 = st.columns([3, 3, 2, 1.2])
        c1.text_input("First Name", key=f"fname_{i}", label_visibility="collapsed", placeholder="John")
        c2.text_input("Last Name",  key=f"lname_{i}", label_visibility="collapsed", placeholder="Doe")
        c3.text_input("SSN",        key=f"ssn_{i}",   label_visibility="collapsed", placeholder="XXX-XX-XXXX")

        if c4.button("Look Up", key=f"lookup_{i}", width="stretch"):
            _do_lookup(i)

        status = row["status"]
        if status == "saved":
            st.markdown(
                "<p style='font-size:12px;color:#10b981;margin:2px 0 4px;"
                "font-family:\"DM Sans\",sans-serif;'>&#10003; Saved successfully</p>",
                unsafe_allow_html=True,
            )
        elif status == "multiple":
            candidates = row.get("candidates", [])
            st.warning(row["message"])
            options = {
                f"{c['FName']} {c['LName']} — ID: {c['PatNum']}, DOB: {c.get('Birthdate') or '—'}, Phone: {c.get('HmPhone') or '—'}": c
                for c in candidates
            }
            selected_label = st.selectbox(
                "Select patient:", list(options.keys()), key=f"select_{i}"
            )
            if st.button("Save Selected", key=f"save_select_{i}"):
                _save_patient(i, options[selected_label], row.get("ssn", ""))
                st.rerun()
        elif status in ("exists", "not_found"):
            st.warning(row["message"])
        elif status == "error":
            st.error(row["message"])

    # ── Add row ─────────────────────────────────────────────────────────────────
    st.markdown("")
    if st.button("+ Add Patient"):
        st.session_state.lookup_rows.append({"status": None, "message": ""})
        st.rerun()

    # ── Navigation ──────────────────────────────────────────────────────────────
    st.markdown("---")
    _, nav_col = st.columns([3, 1])
    with nav_col:
        if st.button("View Export →", type="secondary", width='stretch'):
            st.session_state.page = "export"
            st.rerun()
