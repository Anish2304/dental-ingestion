import asyncio
import concurrent.futures
from core.agents import api_agent, ingest_agent
from utils import logger

log = logger.get("agents.supervisor")


def _run_async(coro):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


def lookup(fname: str, lname: str, ssn: str = "") -> dict:
    log.info("lookup called: fname=%s lname=%s", fname, lname)
    f, l = fname.strip(), lname.strip()
    if not f or not l:
        return {"status": "error", "message": "First and Last Name are required."}

    result = _run_async(api_agent.run(f, l))
    if not result.get("approved"):
        return {"status": "error", "message": result.get("reason", "API agent rejected.")}
    data = result.get("data", [])
    log.info("lookup succeeded for %s %s — %d record(s)", f, l, len(data))
    return {"status": "ok", "data": data, "multiple": len(data) > 1, "message": ""}


def ingest(records: list[dict]) -> dict:
    log.info("ingest called for %d record(s)", len(records))
    if not records:
        return {"status": "error", "message": "No records selected for ingest."}
    if len(records) > 50:
        return {"status": "error", "message": f"Batch too large ({len(records)}). Max 50 per run."}

    result = _run_async(ingest_agent.run(records))
    if not result.get("success"):
        return {"status": "error", "message": result.get("reason", "Ingest agent failed.")}
    log.info("ingest succeeded for %d record(s)", len(records))
    return {"status": "ok", "message": f"Successfully ingested {len(records)} patient(s)."}
