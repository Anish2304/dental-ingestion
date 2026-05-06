import streamlit as st
from db.database import init_db
from views import input_view, export_view

st.set_page_config(
    page_title="Docudent Ingestion Interface",
    page_icon="🗂️",
    layout="wide",
)

init_db()

if "page" not in st.session_state:
    st.session_state.page = "input"

if st.session_state.page == "input":
    input_view.render()
elif st.session_state.page == "export":
    export_view.render()
