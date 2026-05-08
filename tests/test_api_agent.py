"""
Langfuse experiment tests for api_agent.

Mocks _fetch_patient so no real OpenDental API calls are made.
The LLM (Groq) still runs — that is the thing being tested.

Run:
    pytest tests/test_api_agent.py -v
"""

import asyncio
from unittest.mock import AsyncMock, patch

from langfuse import get_client, Evaluation

# ---------------------------------------------------------------------------
# Dataset — each item controls what the mocked API returns and what the
# LLM should decide given that data.
# ---------------------------------------------------------------------------

test_data = [
    {
        "input": {"fname": "john", "lname": "smith"},
        "mock_api": [{"FName": "John", "LName": "Smith", "PatNum": 5}],
        "expected_output": "approved",
        "description": "single valid result",
    },
    {
        "input": {"fname": "ghost", "lname": "user"},
        "mock_api": [],
        "expected_output": "rejected",
        "description": "empty API response — patient not found",
    },
    {
        "input": {"fname": "jo", "lname": "sm"},
        "mock_api": [
            {"FName": "John",   "LName": "Smith", "PatNum": 5},
            {"FName": "Joseph", "LName": "Small", "PatNum": 12},
        ],
        "expected_output": "approved",
        "description": "partial match returning multiple valid results",
    },
    {
        "input": {"fname": "bad", "lname": "data"},
        "mock_api": [{"FName": "Bad", "LName": "Data", "PatNum": None}],
        "expected_output": "rejected",
        "description": "record with null PatNum",
    },
    {
        "input": {"fname": "empty", "lname": "fields"},
        "mock_api": [{"FName": "", "LName": "Fields", "PatNum": 9}],
        "expected_output": "rejected",
        "description": "record with empty FName",
    },
    {
        "input": {"fname": "marvin", "lname": "med"},
        "mock_api": [{"FName": "Marvin", "LName": "Medina", "PatNum": 22}],
        "expected_output": "approved",
        "description": "partial last name match — LLM must not compare query to result",
    },
]


# ---------------------------------------------------------------------------
# Task — runs api_agent.run() with mocked API, returns decision string
# ---------------------------------------------------------------------------

def api_agent_task(*, item, **kwargs):
    from core.agents import api_agent

    async def _run():
        with patch(
            "core.agents.api_agent._fetch_patient",
            new=AsyncMock(return_value=item["mock_api"]),
        ):
            return await api_agent.run(
                item["input"]["fname"],
                item["input"]["lname"],
            )

    result = asyncio.run(_run())
    return "approved" if result.get("approved") else "rejected"


# ---------------------------------------------------------------------------
# Evaluators
# ---------------------------------------------------------------------------

def decision_evaluator(*, output, expected_output, **kwargs):
    return Evaluation(
        name="correct_decision",
        value=1.0 if output == expected_output else 0.0,
    )


def avg_accuracy_evaluator(*, item_results, **kwargs):
    scores = [
        e.value
        for r in item_results
        for e in r.evaluations
        if e.name == "correct_decision"
    ]
    avg = sum(scores) / len(scores) if scores else 0.0
    return Evaluation(
        name="avg_accuracy",
        value=avg,
        comment=f"Accuracy: {avg:.0%} across {len(scores)} case(s)",
    )


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

def test_api_agent_decisions():
    lf = get_client()

    result = lf.run_experiment(
        name="API Agent — Approval Decisions",
        data=test_data,
        task=api_agent_task,
        evaluators=[decision_evaluator],
        run_evaluators=[avg_accuracy_evaluator],
    )

    avg = next(
        (e.value for e in result.run_evaluations if e.name == "avg_accuracy"),
        0.0,
    )

    assert avg >= 0.8, (
        f"API agent accuracy {avg:.0%} is below the 80% threshold. "
        "Check Langfuse dashboard for which cases failed."
    )
