import pytest

from app.agents.analyzer import AnalyzerAgent
from app.models import Source


@pytest.mark.asyncio
async def test_analyzer():

    agent = AnalyzerAgent()

    sources = [
        Source(
            title="Microsoft AI",
            url="https://example.com/microsoft-ai",
            content=(
                "Microsoft invests in artificial intelligence "
                "and provides AI services through Azure."
            ),
        ),
        Source(
            title="Microsoft Azure",
            url="https://example.com/azure",
            content=(
                "Azure provides cloud-based artificial intelligence "
                "and machine learning services."
            ),
        ),
    ]

    result = await agent.analyze(
        company="Microsoft",
        question="What is Microsoft's AI strategy?",
        sources=sources,
    )

    assert result.summary
    assert len(result.key_facts) > 0
    assert len(result.important_points) > 0