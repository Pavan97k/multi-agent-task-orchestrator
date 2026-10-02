import pytest

from app.agents.writer import WriterAgent
from app.models import AnalysisResult


@pytest.mark.asyncio
async def test_writer():

    agent = WriterAgent()

    analysis = AnalysisResult(
        summary="Microsoft is investing heavily in AI.",
        key_facts=[
            "Microsoft provides AI services through Azure.",
            "Microsoft invests in machine learning technologies.",
        ],
        important_points=[
            "AI is an important part of Microsoft's technology strategy."
        ],
    )

    result = await agent.write(
        company="Microsoft",
        question="What is Microsoft's AI strategy?",
        analysis=analysis,
    )

    assert result
    assert "Microsoft" in result
    assert "Summary:" in result
    assert "Key Facts:" in result