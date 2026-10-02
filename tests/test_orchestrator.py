import pytest

from app.orchestrator import TaskOrchestrator


@pytest.mark.asyncio
async def test_orchestrator():

    orchestrator = TaskOrchestrator()

    result = await orchestrator.run(
        company="Microsoft",
        question="What is Microsoft's AI strategy?"
    )

    assert result["company"] == "Microsoft"
    assert result["question"]
    assert result["sources"]
    assert result["analysis"]
    assert result["answer"]