import json
import os
from playwright.sync_api import sync_playwright
from config import FRONTEND_URL
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


def _fill_patient_form(page, p: dict):
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

    print(f"Saved: {p.get('FName')} {p.get('LName')}")


def _inject_into_ui(records: list[dict]):
    if not FRONTEND_URL:
        raise RuntimeError("FRONTEND_URL is not set in environment.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=50)
        context = browser.new_context()
        page = context.new_page()

        # Log all browser console output and errors
        page.on("console", lambda msg: print(f"[browser {msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: print(f"[browser error] {err}"))
        page.on("requestfailed", lambda req: print(f"[request failed] {req.url} - {req.failure}"))

        page.add_init_script("""
            window._API_OVERRIDE = 'http://host.docker.internal:5000/api';
        """)

        page.goto(FRONTEND_URL)
        page.get_by_role("button", name="+ Add New Patient").wait_for(state="visible")

        for record in records:
            _fill_patient_form(page, record)

        browser.close()


def ingest_handler(records: list[dict]) -> None:
    _inject_into_ui(records)
