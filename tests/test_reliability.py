import asyncio

import pytest

from app.orchestrator import TaskOrchestrator


@pytest.mark.asyncio
async def test_retry_success():

    orchestrator = TaskOrchestrator()

    attempts = 0

    async def unstable_operation():

        nonlocal attempts
        attempts += 1

        if attempts < 3:
            raise RuntimeError("Temporary failure")

        return "success"

    result = await orchestrator._run_with_retry(
        unstable_operation,
        retries=2,
        timeout=5,
    )

    assert result == "success"
    assert attempts == 3


@pytest.mark.asyncio
async def test_timeout():

    orchestrator = TaskOrchestrator()

    async def slow_operation():
        await asyncio.sleep(2)
        return "success"

    with pytest.raises(Exception):
        await orchestrator._run_with_retry(
            slow_operation,
            retries=0,
            timeout=0.1,
        )