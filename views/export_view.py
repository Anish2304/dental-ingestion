import pandas as pd
import streamlit as st
from db.crud import get_all_patients, get_all_patients_full, delete_patients_by_ids, log_audit
from core.agents import supervisor

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
                Select records from the database and ingest them.
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

    records, total = get_all_patients(st.session_state.export_page, PAGE_SIZE)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    if not records:
        st.info("No patients in the database. Go back and add some.")
    else:
        df = pd.DataFrame(records)[list(COL_LABELS.keys())]
        df.insert(0, "Select", [r["PatNum"] in st.session_state.checked_ids for r in records])

        column_config = {
            "Select": st.column_config.CheckboxColumn("", width="small"),
            **{k: st.column_config.TextColumn(v) for k, v in COL_LABELS.items()},
        }

        edited = st.data_editor(
            df,
            column_config=column_config,
            width='stretch',
            hide_index=True,
            disabled=list(COL_LABELS.keys()),
            key=f"table_page_{st.session_state.export_page}",
        )

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
            if st.button("← Previous", width='stretch',
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
            if st.button("Next →", width='stretch',
                         disabled=st.session_state.export_page >= total_pages):
                st.session_state.export_page += 1
                st.rerun()

    st.markdown("---")

    selected = sorted(st.session_state.checked_ids)
    # m1, m2, m3 = st.columns(3)
    # m1.metric("Total in Database", total if records else 0)
    # m2.metric("Selected for Ingest", len(selected))
    # m3.metric("Page", f"{st.session_state.export_page} / {total_pages}")

    # st.markdown("")

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
            width="stretch",
        )

    if ingest_clicked:
        full_records = get_all_patients_full()
        full_records = [r for r in full_records if r["PatNum"] in selected]
        log_audit("INGEST", None, {"ingested_ids": selected, "count": len(selected)})
        result = supervisor.ingest(full_records)
        if result["status"] == "error":
            st.error(result["message"])
        else:
            delete_patients_by_ids(selected)
            st.success(result["message"])
            st.session_state.checked_ids.clear()
            st.session_state.export_page = 1

    st.markdown("---")
    if st.button("← Back to Input"):
        st.session_state.page = "input"
        st.session_state.export_page = 1
        st.rerun()
