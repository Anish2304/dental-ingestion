import streamlit as st
from db.database import init_db
from views import export_view, input_view

st.set_page_config(
    page_title="DocuDent AI",
    page_icon="🦷",
    layout="wide",
)

# ── Fonts ──────────────────────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ── Global styles ──────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Fonts */
body, .stApp, input, button, textarea, select, label {
    font-family: 'DM Sans', sans-serif !important;
}
code, pre, [data-testid="stCodeBlock"] * {
    font-family: 'DM Mono', monospace !important;
}

/* Streamlit chrome */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] {
    background: #ffffff !important;
    border-bottom: 1px solid #e5e7eb !important;
    height: 54px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] { background-color: #0f1e3a !important; }
section[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
section[data-testid="stSidebar"] > div:first-child > div { padding-top: 0 !important; }

/* Main content — matches HTML .content { padding: 26px 30px } */
.block-container {
    padding-top: 26px !important;
    padding-left: 30px !important;
    padding-right: 30px !important;
    max-width: 100% !important;
}

/* Primary buttons */
button[kind="primary"],
[data-testid="baseButton-primary"],
[data-testid="stFormSubmitButton"] > button {
    background-color: #2563eb !important;
    border: none !important;
    border-radius: 6px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #ffffff !important;
    font-family: 'DM Sans', sans-serif !important;
}
button[kind="primary"]:hover,
[data-testid="baseButton-primary"]:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    background-color: #1d4ed8 !important;
    color: #ffffff !important;
}

/* Secondary buttons */
button[kind="secondary"],
[data-testid="baseButton-secondary"] {
    border-radius: 6px !important;
    border: 1px solid #e5e7eb !important;
    color: #6b7280 !important;
    background: #ffffff !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    font-family: 'DM Sans', sans-serif !important;
}
button[kind="secondary"]:hover,
[data-testid="baseButton-secondary"]:hover {
    background: #f8fafc !important;
}

/* Form card */
[data-testid="stForm"] {
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
    padding: 16px 20px !important;
    background: #ffffff;
}

/* Text inputs — matches HTML .fi */
.stTextInput input {
    height: 36px !important;
    padding: 0 10px !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 6px !important;
    font-size: 13px !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #111827 !important;
    outline: none !important;
}
.stTextInput input:focus {
    border-color: #2563eb !important;
    box-shadow: none !important;
}

/* Input labels */
.stTextInput label, .stSelectbox label {
    font-size: 11.5px !important;
    font-weight: 600 !important;
    color: #6b7280 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background-color: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    padding: 14px 16px !important;
}
[data-testid="stMetricValue"] {
    font-size: 21px !important;
    font-weight: 700 !important;
    color: #111827 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 12px !important;
    color: #6b7280 !important;
}

/* Dividers */
hr { border-color: #e5e7eb !important; }

/* Caption / helper text */
.stCaption p, [data-testid="stCaptionContainer"] p {
    font-size: 12px !important;
    color: #9ca3af !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Data editor — matches HTML .table-wrap */
[data-testid="stDataEditor"] {
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
    overflow: hidden;
}

/* Hide deploy button */
[data-testid="stToolbar"],
[data-testid="stDeployButton"],
.stDeployButton { display: none !important; }

/* Sidebar width — matches HTML .sidebar { width: 220px; min-width: 220px } */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div:first-child {
    width: 220px !important;
    min-width: 220px !important;
}

/* Confirmation dialog — matches HTML .modal */
[data-testid="stModal"] > div {
    border-radius: 12px !important;
    box-shadow: 0 20px 60px rgba(0,0,0,.18) !important;
    padding: 26px !important;
}
/* Hide dialog built-in close button — only the action button should close */
[data-testid="stModal"] button[data-testid="stBaseButton-headerNoPadding"],
[data-testid="stModal"] button[aria-label="Close"],
[data-testid="stModal"] [data-testid="stModalCloseButton"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ── Demo Account — fixed in topbar (matches HTML .topbar + .account) ───────
st.markdown("""
<div style="position:fixed;top:0;right:0;height:54px;z-index:1000001;
            display:flex;align-items:center;gap:8px;padding:0 28px;">
    <span style="font-size:13px;color:#6b7280;font-family:'DM Sans',sans-serif;">
        Demo Account
    </span>
    <div style="width:30px;height:30px;border-radius:50%;background:#2563eb;
                display:flex;align-items:center;justify-content:center;
                font-size:12px;font-weight:700;color:#ffffff;flex-shrink:0;">DA</div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo — matches HTML .logo
    st.markdown("""
    <div style="padding:22px 20px 18px;border-bottom:1px solid rgba(255,255,255,.06);">
        <span style="font-size:17px;font-weight:700;color:#ffffff;
                     font-family:'DM Sans',sans-serif;">
            DOCU<span style="color:#3b82f6;">DENT</span>.AI
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Nav — matches HTML .nav + .nav-item.active
    st.markdown("""
    <div style="padding:12px 10px;">
        <div style="display:flex;align-items:center;gap:10px;
                    padding:10px 12px;border-radius:8px;background:#1e3560;">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
                 viewBox="0 0 24 24" fill="none" stroke="white"
                 stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"
                 style="flex-shrink:0;">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <line x1="19" y1="8" x2="19" y2="14"/>
                <polyline points="17 12 19 14 21 12"/>
            </svg>
            <span style="font-size:14px;font-weight:500;color:#ffffff;
                         font-family:'DM Sans',sans-serif;">
                Patient Import
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Init + routing ─────────────────────────────────────────────────────────
init_db()

if "page" not in st.session_state:
    st.session_state.page = "input"

if st.session_state.page == "input":
    input_view.render()
elif st.session_state.page == "export":
    export_view.render()
