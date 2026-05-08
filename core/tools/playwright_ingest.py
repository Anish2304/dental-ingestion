import os
import sys
import asyncio
from playwright.async_api import async_playwright
from config import FRONTEND_URL
from utils import logger

log = logger.get("tools.playwright_ingest")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

_STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
HTML_PATH = f"file:///{os.path.abspath(os.path.join(_STATIC_DIR, 'frontend.html'))}"

_CONCURRENCY = 5  # max parallel pages


async def _fill_patient_form(page, p: dict):
    patient_ref = f"{p.get('FName')} {p.get('LName')}"
    log.debug("Filling form for: %s", patient_ref)

    add_btn = page.get_by_role("button", name="+ Add New Patient")
    await add_btn.wait_for(state="visible")
    await add_btn.click()

    await page.wait_for_selector("#f_fname", state="visible")

    await page.fill("#f_fname",   p.get("FName", ""))
    await page.fill("#f_lname",   p.get("LName", ""))
    await page.fill("#f_dob",     p.get("Birthdate", ""))
    await page.fill("#f_ssn",     p.get("SSN", ""))
    await page.fill("#f_phone",   p.get("HmPhone", ""))
    await page.fill("#f_prov",    p.get("priProvAbbr", ""))
    await page.fill("#f_address", p.get("Address", ""))
    await page.fill("#f_city",    p.get("City", ""))
    await page.fill("#f_state",   p.get("State", ""))
    await page.fill("#f_zip",     p.get("Zip", ""))
    await page.fill("#f_email",   p.get("Email", ""))

    await page.get_by_role("button", name="Save Patient").click()
    await page.wait_for_function("!document.getElementById('addModal').classList.contains('open')")

    log.info("Form submitted for: %s", patient_ref)


async def _fill_one(context, record: dict, semaphore: asyncio.Semaphore):
    async with semaphore:
        page = await context.new_page()
        try:
            await page.goto(HTML_PATH)
            await _fill_patient_form(page, record)
        finally:
            await page.close()


async def _inject_into_ui(records: list[dict]):
    target = HTML_PATH
    log.info("Launching Playwright for %d record(s) → %s", len(records), target)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context()
        semaphore = asyncio.Semaphore(_CONCURRENCY)

        await asyncio.gather(*[_fill_one(context, r, semaphore) for r in records])

        await browser.close()

    log.info("Playwright ingest finished — %d record(s) submitted", len(records))


async def ingest_handler(records: list[dict]) -> None:
    await _inject_into_ui(records)
