import asyncio
import concurrent.futures
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from core.agents import api_agent, ingest_agent
from utils import logger

log = logger.get("agents.supervisor")


class State(TypedDict):
    task: str
    fname: str
    lname: str
    ssn: str
    records: list
    result: dict
    next: str  # set by supervisor node, read by conditional edge


# ── Supervisor node — guardrails + routing decision ────────────────────────────

def _supervisor_node(state: State) -> dict:
    task = state["task"]
    log.info("Supervisor received task='%s'", task)

    if task == "lookup":
        f, l = state["fname"].strip(), state["lname"].strip()
        if not f or not l:
            log.warning("Supervisor blocked lookup: missing name fields")
            return {"next": "end", "result": {"_error": "First and Last Name are required."}}
        if len(f) < 2 or len(l) < 2:
            log.warning("Supervisor blocked lookup: name too short (%s %s)", f, l)
            return {"next": "end", "result": {"_error": "Names must be at least 2 characters."}}
        log.info("Supervisor approved lookup → api_agent: %s %s", f, l)
        return {"next": "api_agent"}

    if task == "ingest":
        r = state.get("records", [])
        if not r:
            log.warning("Supervisor blocked ingest: no records provided")
            return {"next": "end", "result": {"_error": "No records selected for ingest."}}
        if len(r) > 50:
            log.warning("Supervisor blocked ingest: batch size %d exceeds limit", len(r))
            return {"next": "end", "result": {"_error": f"Batch too large ({len(r)}). Max 50 per run."}}
        log.info("Supervisor approved ingest → ingest_agent: %d record(s)", len(r))
        return {"next": "ingest_agent"}

    log.error("Supervisor: unknown task='%s'", task)
    return {"next": "end", "result": {"_error": f"Unknown task: {task}"}}


# ── Agent nodes ────────────────────────────────────────────────────────────────

async def _api_agent_node(state: State) -> dict:
    log.info("api_agent_node running for: %s %s", state["fname"], state["lname"])
    result = await api_agent.run(state["fname"], state["lname"])
    return {"result": result}


async def _ingest_agent_node(state: State) -> dict:
    log.info("ingest_agent_node running for %d record(s)", len(state["records"]))
    result = await ingest_agent.run(state["records"])
    return {"result": result}


# ── Conditional edge — reads supervisor's routing decision ─────────────────────

def _route(state: State) -> str:
    return state.get("next", "end")


# ── Graph ──────────────────────────────────────────────────────────────────────

_builder = StateGraph(State)
_builder.add_node("supervisor", _supervisor_node)
_builder.add_node("api_agent", _api_agent_node)
_builder.add_node("ingest_agent", _ingest_agent_node)

_builder.add_edge(START, "supervisor")
_builder.add_conditional_edges("supervisor", _route, {
    "api_agent": "api_agent",
    "ingest_agent": "ingest_agent",
    "end": END,
})
_builder.add_edge("api_agent", END)
_builder.add_edge("ingest_agent", END)

_graph = _builder.compile()


# ── Public sync interface (called from Streamlit) ──────────────────────────────

def _run_async(coro):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


def lookup(fname: str, lname: str, ssn: str = "") -> dict:
    log.info("supervisor.lookup called: fname=%s lname=%s", fname, lname)
    state = _run_async(_graph.ainvoke({
        "task": "lookup", "fname": fname, "lname": lname,
        "ssn": ssn, "records": [], "result": {}, "next": "",
    }))
    result = state["result"]
    if "_error" in result:
        return {"status": "error", "message": result["_error"]}
    if not result.get("approved"):
        return {"status": "error", "message": result.get("reason", "API agent rejected.")}
    log.info("supervisor.lookup succeeded for %s %s", fname, lname)
    return {"status": "ok", "data": result.get("data"), "message": ""}


def ingest(records: list[dict]) -> dict:
    log.info("supervisor.ingest called for %d record(s)", len(records))
    state = _run_async(_graph.ainvoke({
        "task": "ingest", "fname": "", "lname": "",
        "ssn": "", "records": records, "result": {}, "next": "",
    }))
    result = state["result"]
    if "_error" in result:
        return {"status": "error", "message": result["_error"]}
    if not result.get("success"):
        return {"status": "error", "message": result.get("reason", "Ingest agent failed.")}
    log.info("supervisor.ingest succeeded for %d record(s)", len(records))
    return {"status": "ok", "message": f"Successfully ingested {len(records)} patient(s)."}
