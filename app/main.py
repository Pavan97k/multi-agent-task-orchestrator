import json

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from app.models import TaskRequest
from app.orchestrator import TaskOrchestrator


app = FastAPI(
    title="Multi-Agent Task Orchestrator"
)

orchestrator = TaskOrchestrator()


@app.get("/")
async def root():

    return {
        "message": "Multi-Agent Task Orchestrator is running"
    }


@app.post("/task")
async def create_task(
    request: TaskRequest,
):

    result = await orchestrator.run(
        company=request.company,
        question=request.question,
    )

    return result


@app.post("/task/stream")
async def stream_task(
    request: TaskRequest,
):

    async def event_generator():

        async for event in orchestrator.stream(
            company=request.company,
            question=request.question,
        ):

            data = json.dumps(event)

            yield f"data: {data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )