import json
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from core.tools.opendental import fetch_patient as _fetch_patient
from utils import logger

log = logger.get("agents.api_agent")

_llm = ChatGroq(model="llama-3.3-70b-versatile")

_PROMPT = (
    "You are an API agent for a dental records system. "
    "Use fetch_patient to retrieve patient data. "
    "The API performs partial, case-insensitive matching — returned names will not exactly match the query. "
    "Your only job is to check that every returned record has non-empty FName, LName, and PatNum. "
    "Do NOT compare query names to returned names. "
    "Approve if at least one valid record is returned, reject only if the list is empty or all records are missing required fields. "
    'Respond ONLY with JSON: {"approved": bool, "reason": <string>}'
)


async def run(fname: str, lname: str) -> dict:
    """Fetch and validate a patient via the OpenDental API.

    Raw normalized data is stored in the closure so Claude only validates
    (approved/reason) — it never reconstructs field values.
    """
    log.info("api_agent.run called for: %s %s", fname, lname)
    _raw: list[dict] = []

    @tool
    async def fetch_patient(fname: str, lname: str) -> str:
        """Query the OpenDental API for a patient by first and last name."""
        log.debug("Tool fetch_patient called: fname=%s lname=%s", fname, lname)
        try:
            results = await _fetch_patient(fname, lname)
            _raw.extend(results)
            summary = [
                {"FName": r.get("FName"), "LName": r.get("LName"), "PatNum": r.get("PatNum")}
                for r in results
            ]
            log.debug("fetch_patient tool returning %d result(s) to agent", len(summary))
            return json.dumps(summary)
        except Exception as e:
            log.error("fetch_patient tool error: %s", e, exc_info=True)
            return json.dumps({"error": str(e)})

    agent = create_react_agent(_llm, tools=[fetch_patient], prompt=_PROMPT)

    try:
        result = await agent.ainvoke({
            "messages": [("user", f"Look up patient {fname} {lname} and validate the result.")]
        })
    except Exception as e:
        log.error("Agent invocation failed for %s %s: %s", fname, lname, e, exc_info=True)
        return {"approved": False, "data": None, "reason": f"Agent error: {e}"}

    last = result["messages"][-1].content
    log.debug("Agent raw response: %s", last)

    try:
        decision = json.loads(last)
    except json.JSONDecodeError:
        log.warning("Agent response was not valid JSON for %s %s: %s", fname, lname, last)
        decision = {"approved": False, "reason": last}

    if decision.get("approved") and _raw:
        decision["data"] = _raw
        log.info("api_agent approved %d record(s) for %s %s", len(_raw), fname, lname)
    else:
        log.warning("api_agent rejected lookup for %s %s: %s", fname, lname, decision.get("reason"))
        decision["data"] = []

    return decision
