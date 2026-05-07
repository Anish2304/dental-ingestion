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
    "Check the result has non-empty FName, LName, and PatNum. "
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
    def fetch_patient(fname: str, lname: str) -> str:
        """Query the OpenDental API for a patient by first and last name."""
        log.debug("Tool fetch_patient called: fname=%s lname=%s", fname, lname)
        try:
            results = _fetch_patient(fname, lname)
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
        decision["data"] = _raw[0]
        log.info("api_agent approved patient %s %s (PatNum=%s)", fname, lname, _raw[0].get("PatNum"))
    elif not decision.get("approved"):
        log.warning("api_agent rejected lookup for %s %s: %s", fname, lname, decision.get("reason"))
        decision["data"] = None

    return decision
