import pytest

from app.agents.retriever import RetrieverAgent


@pytest.mark.asyncio
async def test_retriever():
    agent = RetrieverAgent()

    sources = await agent.retrieve(
        "Microsoft",
        "artificial intelligence"
    )

    assert isinstance(sources, list)
    assert len(sources) > 0
    assert sources[0].title
    assert sources[0].url