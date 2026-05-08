"""
Langfuse experiment tests for ingest_agent.

Mocks _ingest_handler so no Playwright browser is launched.
The LLM (Groq) still runs — that is the thing being tested.

Note: the ingest_agent LLM is currently doing deterministic validation
(FName/LName present check). These tests will pass at near 100% but
serve as a regression baseline — if the prompt is changed, scores here
will reflect the impact.

Run:
    pytest tests/test_ingest_agent.py -v
"""

import asyncio
from unittest.mock import AsyncMock, patch

from langfuse import get_client, Evaluation

# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

test_data = [
    {
        "input": [{"PatNum": 1, "FName": "John", "LName": "Smith"}],
        "expected_output": "success",
        "description": "single valid record",
    },
    {
        "input": [
            {"PatNum": 2, "FName": "Alice", "LName": "Lee"},
            {"PatNum": 3, "FName": "Bob",   "LName": "Jones"},
        ],
        "expected_output": "success",
        "description": "batch of two valid records",
    },
    {
        "input": [{"PatNum": 4, "FName": "", "LName": "Jones"}],
        "expected_output": "failed",
        "description": "missing FName",
    },
    {
        "input": [{"PatNum": 5, "FName": "Alice", "LName": ""}],
        "expected_output": "failed",
        "description": "missing LName",
    },
    {
        "input": [
            {"PatNum": 6, "FName": "Alice", "LName": "Lee"},
            {"PatNum": 7, "FName": "",      "LName": "Bad"},
        ],
        "expected_output": "failed",
        "description": "one invalid record in a batch blocks the whole ingest",
    },
    {
        "input": [],
        "expected_output": "failed",
        "description": "empty batch",
    },
]


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

def ingest_agent_task(*, item, **kwargs):
    from core.agents import ingest_agent

    async def _run():
        with patch(
            "core.agents.ingest_agent._ingest_handler",
            new=AsyncMock(return_value=None),
        ):
            return await ingest_agent.run(item["input"])

    result = asyncio.run(_run())
    return "success" if result.get("success") else "failed"


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

def test_ingest_agent_validation():
    lf = get_client()

    result = lf.run_experiment(
        name="Ingest Agent — Validation Decisions",
        data=test_data,
        task=ingest_agent_task,
        evaluators=[decision_evaluator],
        run_evaluators=[avg_accuracy_evaluator],
    )

    avg = next(
        (e.value for e in result.run_evaluations if e.name == "avg_accuracy"),
        0.0,
    )

    assert avg >= 0.8, (
        f"Ingest agent accuracy {avg:.0%} is below the 80% threshold. "
        "Check Langfuse dashboard for which cases failed."
    )
