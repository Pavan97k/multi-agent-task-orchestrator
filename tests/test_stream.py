import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_stream_endpoint():

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        response = await client.post(
            "/task/stream",
            json={
                "company": "Microsoft",
                "question": "What is Microsoft's AI strategy?",
            },
        )

    assert response.status_code == 200

    assert response.headers["content-type"].startswith(
        "text/event-stream"
    )

    assert "retriever" in response.text
    assert "analyzer" in response.text
    assert "writer" in response.text
    assert "orchestrator" in response.text

    assert "Task completed successfully" in response.text