import json
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from core.tools.playwright_ingest import ingest_handler as _ingest_handler
from utils import logger

log = logger.get("agents.ingest_agent")

_llm = ChatGroq(model="llama-3.3-70b-versatile")

_PROMPT = (
    "You are an ingest agent for a dental records system. "
    "Check every record has non-empty FName and LName. "
    "If valid, call ingest_patients with confirmed=true. "
    'Respond ONLY with JSON: {"success": bool, "reason": <string>}'
)


async def run(records: list[dict]) -> dict:
    log.info("ingest_agent.run called with %d record(s)", len(records))

    @tool
    async def ingest_patients(confirmed: bool) -> str:
        """Trigger Playwright to submit patient records into the dental frontend. Only call if all records have FName and LName."""
        log.debug("Tool ingest_patients called with confirmed=%s", confirmed)
        if not confirmed:
            log.warning("ingest_patients called with confirmed=False — aborting")
            return json.dumps({"error": "Validation failed — not confirmed."})
        try:
            log.info("Triggering Playwright ingest for %d record(s)", len(records))
            await _ingest_handler(records)
            log.info("Playwright ingest completed successfully for %d record(s)", len(records))
            return json.dumps({"status": "success"})
        except Exception as e:
            log.error("Playwright ingest failed: %s", e, exc_info=True)
            return json.dumps({"error": str(e)})

    agent = create_react_agent(_llm, tools=[ingest_patients], prompt=_PROMPT)

    summary = json.dumps([
        {k: r.get(k, "") for k in ["PatNum", "FName", "LName"]}
        for r in records
    ])
    log.debug("Sending record summary to agent: %s", summary)

    try:
        result = await agent.ainvoke({
            "messages": [("user", f"Validate and ingest {len(records)} patient(s). Records: {summary}")]
        })
    except Exception as e:
        log.error("Agent invocation failed: %s", e, exc_info=True)
        return {"success": False, "reason": f"Agent error: {e}"}

    last = result["messages"][-1].content
    log.debug("Agent raw response: %s", last)

    try:
        decision = json.loads(last)
    except json.JSONDecodeError:
        log.warning("Agent response was not valid JSON: %s", last)
        decision = {"success": False, "reason": last}

    if decision.get("success"):
        log.info("ingest_agent completed successfully for %d record(s)", len(records))
    else:
        log.warning("ingest_agent failed: %s", decision.get("reason"))

    return decision
