import json
import os
from playwright.sync_api import sync_playwright

HTML_PATH = f"file:///{os.path.abspath('frontend.html')}"
# HTML_PATH = "frontend.html"

def fill_patient_form(page, p):

    # Click Add Patient button properly
    add_btn = page.get_by_role("button", name="+ Add New Patient")
    add_btn.wait_for(state="visible")
    add_btn.click()

    # Wait for form to be visible
    page.wait_for_selector("#f_fname", state="visible")

    # Fill form
    page.fill("#f_fname", p.get("FName", ""))
    page.fill("#f_lname", p.get("LName", ""))
    page.fill("#f_dob", p.get("Birthdate", ""))
    page.fill("#f_ssn", p.get("SSN", ""))
    page.fill("#f_phone", p.get("HmPhone", ""))
    page.fill("#f_prov", p.get("priProvAbbr", ""))
    page.fill("#f_address", p.get("Address", ""))
    page.fill("#f_city", p.get("City", ""))
    page.fill("#f_state", p.get("State", ""))
    page.fill("#f_zip", p.get("Zip", ""))
    page.fill("#f_email", p.get("Email", ""))

    # Click Save
    save_btn = page.get_by_role("button", name="Save Patient")
    save_btn.click()

    # Wait for modal to close (overlay loses 'open' class, f_fname stays in DOM)
    page.wait_for_function("!document.getElementById('addModal').classList.contains('open')")

    print(f"✅ Saved: {p.get('FName')} {p.get('LName')}")

# ---------------- PLAYWRIGHT RUNNER ----------------
def inject_into_ui(data):

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            slow_mo=50  # helps debugging timing issues
            )
        context = browser.new_context()

        page = context.new_page()
        page.goto(HTML_PATH)
        page.get_by_role("button", name="+ Add New Patient").wait_for(state="visible")
        # page.wait_for_timeout(2000)
        # page.wait_for_selector("#patientsTbody")

        print("🚀 Starting form automation...")

        # 🔥 REAL UI ACTION LOOP
        for record in data:
            fill_patient_form(page, record)

        print("✅ All patients inserted")

        browser.close()


# ---------------- INGEST HANDLER ----------------
def ingest_handler(records: list[dict]) -> str:

    output = json.dumps(records, indent=2)
    print(output)

    # 🔥 Trigger Playwright automation
    inject_into_ui(records)

    return output
 



