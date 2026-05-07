import os
import asyncio
import sys
from playwright.sync_api import sync_playwright
from config import FRONTEND_URL
from utils import logger

log = logger.get("tools.playwright_ingest")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

_STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
HTML_PATH = f"file:///{os.path.abspath(os.path.join(_STATIC_DIR, 'frontend.html'))}"


def _fill_patient_form(page, p: dict):
    patient_ref = f"{p.get('FName')} {p.get('LName')}"
    log.debug("Filling form for: %s", patient_ref)

    add_btn = page.get_by_role("button", name="+ Add New Patient")
    add_btn.wait_for(state="visible")
    add_btn.click()

    page.wait_for_selector("#f_fname", state="visible")

    page.fill("#f_fname",   p.get("FName", ""))
    page.fill("#f_lname",   p.get("LName", ""))
    page.fill("#f_dob",     p.get("Birthdate", ""))
    page.fill("#f_ssn",     p.get("SSN", ""))
    page.fill("#f_phone",   p.get("HmPhone", ""))
    page.fill("#f_prov",    p.get("priProvAbbr", ""))
    page.fill("#f_address", p.get("Address", ""))
    page.fill("#f_city",    p.get("City", ""))
    page.fill("#f_state",   p.get("State", ""))
    page.fill("#f_zip",     p.get("Zip", ""))
    page.fill("#f_email",   p.get("Email", ""))

    page.get_by_role("button", name="Save Patient").click()
    page.wait_for_function("!document.getElementById('addModal').classList.contains('open')")

    log.info("Form submitted for: %s", patient_ref)


def _inject_into_ui(records: list[dict]):
    target =  HTML_PATH
    # target = FRONTEND_URL if FRONTEND_URL else
    log.info("Launching Playwright for %d record(s) → %s", len(records), target)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=50)
        context = browser.new_context()
        page = context.new_page()

        page.on("console", lambda msg: log.debug("[browser %s] %s", msg.type, msg.text))
        page.on("pageerror", lambda err: log.error("[browser error] %s", err))
        page.on("requestfailed", lambda req: log.warning("[request failed] %s — %s", req.url, req.failure))

        page.goto(target)
        page.get_by_role("button", name="+ Add New Patient").wait_for(state="visible")

        for record in records:
            _fill_patient_form(page, record)

        browser.close()

    log.info("Playwright ingest finished — %d record(s) submitted", len(records))


def ingest_handler(records: list[dict]) -> None:
    _inject_into_ui(records)
