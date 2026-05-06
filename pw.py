# from playwright.sync_api import sync_playwright
 
# HTML_PATH = "frontend.html"
# STREAMLIT_URL = "http://localhost:8501"
# API_KEYWORD = "/data"   # 🔁 change if your endpoint differs
 
# def normalize_payload(payload):
#     # Always return list
#     if isinstance(payload, list):
#         return payload
#     elif isinstance(payload, dict):
#         return [payload]
#     return []
 
# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=False)
#     context = browser.new_context()
 
#     # ✅ Open your HTML UI
#     ui_page = context.new_page()
#     ui_page.goto(HTML_PATH)
#     ui_page.wait_for_selector("#patientsTbody")
 
#     # ❗ IMPORTANT: Disable API auto-load in your HTML
#     ui_page.evaluate("window.loadPatients = () => {};")
 
#     # ✅ Open Streamlit inside SAME context
#     streamlit_page = context.new_page()
#     streamlit_page.goto(STREAMLIT_URL)
 
#     print("👂 Listening for Streamlit API calls...")
 
#     def handle_request(request):
#         try:
#             if API_KEYWORD in request.url and request.method == "POST":
#                 payload = request.post_data_json
#                 data = normalize_payload(payload)
 
#                 print("🚀 New data received:", data)
 
#                 # ✅ Inject into YOUR HTML structure
#                 ui_page.evaluate(
#                     """(data) => {
 
#                         // Replace existing dataset
#                         window.allPatients = data;
#                         window.filtered = [...data];
#                         window.currentPage = 1;
 
#                         // Re-render table using your existing function
#                         if (typeof renderTable === 'function') {
#                             renderTable();
#                         }
 
#                     }""",
#                     data
#                 )
 
#         except Exception as e:
#             print("❌ Error:", e)
 
#     # 🔥 Listen at CONTEXT level (important)
#     context.on("request", handle_request)
 
#     print("👉 Click 'Inject Data' in Streamlit")
 
#     streamlit_page.wait_for_timeout(0)

# import os
# from playwright.sync_api import sync_playwright

# # ✅ Convert local HTML file to proper file:// URL
# HTML_PATH = f"file:///{os.path.abspath('frontend.html')}"
# STREAMLIT_URL = "http://localhost:8501"
# API_KEYWORD = "/data"   # 🔁 change if your endpoint differs


# def normalize_payload(payload):
#     # Always return list
#     if isinstance(payload, list):
#         return payload
#     elif isinstance(payload, dict):
#         return [payload]
#     return []


# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=False)
#     context = browser.new_context()

#     # ✅ Open your HTML UI
#     ui_page = context.new_page()
#     ui_page.goto(HTML_PATH)
#     ui_page.wait_for_selector("#patientsTbody")

#     # ❗ Disable auto API call if your HTML does it
#     ui_page.evaluate("window.loadPatients = () => {};")

#     # ✅ Open Streamlit in same browser context
#     streamlit_page = context.new_page()
#     streamlit_page.goto(STREAMLIT_URL)

#     print("👂 Listening for Streamlit API calls...")

#     def handle_request(request):
#         try:
#             if API_KEYWORD in request.url and request.method == "POST":
                
#                 # ✅ Safely parse payload
#                 payload = request.post_data_json
#                 data = normalize_payload(payload)

#                 print("🚀 New data received:", data)

#                 # ✅ Inject into HTML page
#                 ui_page.evaluate(
#                     """(data) => {
#                         window.allPatients = data;
#                         window.filtered = [...data];
#                         window.currentPage = 1;

#                         if (typeof renderTable === 'function') {
#                             renderTable();
#                         }
#                     }""",
#                     data
#                 )

#         except Exception as e:
#             print("❌ Error handling request:", e)

#     # 🔥 Listen at CONTEXT level (important)
#     context.on("request", handle_request)

#     print("👉 Click 'Inject Data' in Streamlit")

#     # ✅ Keep script alive
#     input("Press ENTER to exit...")


import json
import os
from playwright.sync_api import sync_playwright

HTML_PATH = f"file:///{os.path.abspath('frontend.html')}"


def inject_into_ui(data):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        page = context.new_page()
        page.goto(HTML_PATH)
        page.wait_for_selector("#patientsTbody")

        # Inject data into UI
        page.evaluate(
            """(data) => {
                window.allPatients = data;
                window.filtered = [...data];
                window.currentPage = 1;

                if (typeof renderTable === 'function') {
                    renderTable();
                }
            }""",
            data
        )

        print("✅ Data injected into UI")

        # Keep browser open for 5 minutes, then close
        page.wait_for_timeout(300_000)
        browser.close()


def ingest_handler_pw(records: list[dict]) -> str:
    inject_into_ui(records)

