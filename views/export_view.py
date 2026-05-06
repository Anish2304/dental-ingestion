import pandas as pd
import streamlit as st
from db.crud import get_session_patients, get_patients_by_ids, log_audit
from ingest import ingest_handler
from pw import ingest_handler_pw

PAGE_SIZE = 10

COL_LABELS = {
    "PatNum":      "Patient ID",
    "FName":       "First Name",
    "LName":       "Last Name",
    "MiddleI":     "MI",
    "SSN":         "SSN",
    "Birthdate":   "Date of Birth",
    "HmPhone":     "Phone",
    "Email":       "Email",
    "PatStatus":   "Status",
    "BillingType": "Billing Type",
}


def render():
    st.markdown(
        """
        <div style="padding: 1.5rem 0 0.5rem 0;">
            <h1 style="margin: 0; font-size: 2rem; font-weight: 700; letter-spacing: -0.5px;">
                Patient Export
            </h1>
            <p style="margin: 0.25rem 0 0 0; color: grey; font-size: 0.95rem;">
                Select records added this session and ingest them.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    if "export_page" not in st.session_state:
        st.session_state.export_page = 1
    if "checked_ids" not in st.session_state:
        st.session_state.checked_ids = set()

    session_ids = st.session_state.get("session_pat_nums", [])
    records, total = get_session_patients(session_ids, st.session_state.export_page, PAGE_SIZE)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    if not records:
        st.info("No patients added this session. Go back and add some.")
    else:
        # ── Table (render first so sync runs before we read checked_ids) ────
        df = pd.DataFrame(records)[list(COL_LABELS.keys())]
        df.insert(0, "Select", [r["PatNum"] in st.session_state.checked_ids for r in records])

        column_config = {
            "Select": st.column_config.CheckboxColumn("", width="small"),
            **{k: st.column_config.TextColumn(v) for k, v in COL_LABELS.items()},
        }

        edited = st.data_editor(
            df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            disabled=list(COL_LABELS.keys()),
            key=f"table_page_{st.session_state.export_page}",
        )

        # Sync checkbox state back immediately — must happen before any count read
        for _, row in edited.iterrows():
            pat_num = int(row["PatNum"])
            if row["Select"]:
                st.session_state.checked_ids.add(pat_num)
            else:
                st.session_state.checked_ids.discard(pat_num)

        # ── Pagination ───────────────────────────────────────────────────────
        st.markdown("")
        pcol1, pcol2, pcol3 = st.columns([1, 4, 1])
        with pcol1:
            if st.button("← Previous", use_container_width=True,
                         disabled=st.session_state.export_page <= 1):
                st.session_state.export_page -= 1
                st.rerun()
        with pcol2:
            chosen = st.selectbox(
                "Go to page",
                list(range(1, total_pages + 1)),
                index=st.session_state.export_page - 1,
                label_visibility="collapsed",
            )
            if chosen != st.session_state.export_page:
                st.session_state.export_page = chosen
                st.rerun()
        with pcol3:
            if st.button("Next →", use_container_width=True,
                         disabled=st.session_state.export_page >= total_pages):
                st.session_state.export_page += 1
                st.rerun()

    st.markdown("---")

    # ── Metrics — read AFTER sync so counts are accurate ────────────────────
    selected = sorted(st.session_state.checked_ids)
    m1, m2, m3 = st.columns(3)
    m1.metric("Total This Session", len(session_ids))
    m2.metric("Selected for Ingest", len(selected))
    m3.metric("Page", f"{st.session_state.export_page} / {total_pages}")

    st.markdown("")

    # ── Ingest action ────────────────────────────────────────────────────────
    bc1, bc2 = st.columns([3, 1])
    with bc1:
        if selected:
            st.markdown(f"**{len(selected)}** patient(s) ready to ingest.")
        else:
            st.markdown("_Check rows above to select patients for ingest._")
    with bc2:
        ingest_clicked = st.button(
            "Ingest Selected", type="primary",
            disabled=len(selected) == 0,
            use_container_width=True,
        )

    if ingest_clicked:
        full_records = get_patients_by_ids(selected)
        log_audit("INGEST", None, {"ingested_ids": selected, "count": len(selected)})
        output = ingest_handler(full_records)
        # ingest_handler_pw(full_records)
        # from patient_db_writer import write_ingested_patients
        # write_ingested_patients(full_records)
        st.success(f"Successfully ingested {len(full_records)} patient(s).")
        with st.expander("JSON sent to ingest module", expanded=True):
            st.code(output, language="json")
        st.session_state.checked_ids.clear()
        st.session_state.session_pat_nums = [
            p for p in st.session_state.get("session_pat_nums", [])
            if p not in selected
        ]
        st.session_state.export_page = 1

    st.markdown("---")
    if st.button("← Back to Input"):
        st.session_state.page = "input"
        st.session_state.export_page = 1
        st.rerun()
