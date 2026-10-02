# Multi-Agent Task Orchestrator

A lightweight multi-agent task orchestration system built with Python and FastAPI.

The system receives a task containing a company and a question, then coordinates three specialized agents:

1. Retriever Agent — retrieves relevant source material
2. Analyzer Agent — analyzes the retrieved information using an LLM
3. Writer Agent — converts the structured analysis into a final response

The agents are coordinated by a custom asynchronous orchestrator without using frameworks such as LangGraph, CrewAI, or AutoGen.

---

## Architecture

```text
Client
   |
   v
FastAPI
   |
   v
Task Orchestrator
   |
   +------------------+
   |                  |
   v                  |
Retriever Agent       |
   |                  |
   v                  |
Analyzer Agent        |
   |                  |
   v                  |
Writer Agent          |
   |                  |
   +------------------+
          |
          v
      Final Result

      Agent Responsibilities
1. Retriever Agent

File:

app/agents/retriever.py

Responsibility:

Collect source material related to the requested company and question.
Return sources using the Source Pydantic model.
Keep source retrieval separate from analysis.

The current implementation uses controlled demo source data so that the orchestration pipeline remains deterministic and does not depend on an external search service.

2. Analyzer Agent

File:

app/agents/analyzer.py

Responsibility:

Receive the sources produced by the Retriever Agent.
Send the source material to an LLM through the Groq API.
Extract:
Summary
Key facts
Important points
Return a validated AnalysisResult.

The analyzer is instructed to use only the supplied source material and avoid inventing facts.

3. Writer Agent

File:

app/agents/writer.py

Responsibility:

Receive the structured analysis.
Convert it into a concise human-readable response.
It does not perform retrieval or independent analysis.

This separation keeps the writer focused on presentation.

Orchestration Flow

The workflow is intentionally sequential because each stage depends on the output of the previous stage.

Task Request
     |
     v
Retriever
     |
     | sources
     v
Analyzer
     |
     | structured analysis
     v
Writer
     |
     v
Final Answer

The orchestrator is implemented in:

app/orchestrator.py

The orchestration code uses Python's asyncio capabilities.

Reliability

The orchestrator includes explicit reliability handling.

Retry

Temporary agent failures can be retried.

The current configuration allows:

2 retries
Timeout

Each operation can be protected using an asynchronous timeout.

Current default:

15 seconds
Graceful Degradation

If an agent fails after retry attempts:

The orchestrator does not unnecessarily crash the complete request.
Fallback information is returned where possible.
Streaming requests emit failure events so the client can understand which stage failed.

This makes failures visible instead of silently hiding them.

Server-Sent Events

The project provides a streaming endpoint:

POST /task/stream

The endpoint emits progress events such as:

retriever started
retriever completed
analyzer started
analyzer completed
writer started
writer completed
orchestrator completed

Each event is sent using the Server-Sent Events format:

data: {...}

This allows a client to observe the progress of the multi-agent workflow instead of waiting silently for the complete response.

API Endpoints
Health Check
GET /

Response:

{
  "message": "Multi-Agent Task Orchestrator is running"
}
Run Task
POST /task

Request:

{
  "company": "Microsoft",
  "question": "What is Microsoft's AI strategy?"
}
Stream Task Progress
POST /task/stream

Request:

{
  "company": "Microsoft",
  "question": "What is Microsoft's AI strategy?"
}

The response uses:

Content-Type: text/event-stream
Project Structure
multi-agent-task-orchestrator/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── orchestrator.py
│   │
│   └── agents/
│       ├── __init__.py
│       ├── retriever.py
│       ├── analyzer.py
│       └── writer.py
│
├── tests/
│   ├── test_retriever.py
│   ├── test_analyzer.py
│   ├── test_writer.py
│   ├── test_orchestrator.py
│   ├── test_reliability.py
│   └── test_stream.py
│
├── .env
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
Technology Stack
Python
FastAPI
Pydantic
asyncio
Server-Sent Events
Groq API
AsyncGroq
pytest
pytest-asyncio
httpx

No multi-agent orchestration framework is used.

The orchestration logic is implemented directly using Python and asyncio.

Setup
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd multi-agent-task-orchestrator
2. Create a virtual environment
python -m venv venv
3. Activate the virtual environment

Windows PowerShell:

.\venv\Scripts\Activate.ps1
4. Install dependencies
pip install -r requirements.txt
5. Configure environment variables

Create a .env file in the project root:

GROQ_API_KEY=your_groq_api_key_here

Never commit the .env file to GitHub.

The project already includes .env in .gitignore.

Run the Application

Start the FastAPI server:

uvicorn app.main:app --reload

The API will be available at:

http://127.0.0.1:8000

FastAPI documentation:

http://127.0.0.1:8000/docs
Run Tests

Run the complete test suite:

python -m pytest -v

The test suite covers:

Retriever behavior
Analyzer behavior
Writer behavior
Orchestrator workflow
Retry behavior
Timeout behavior
SSE streaming endpoint
Design Decisions
Why separate agents?

Each agent has one clear responsibility.

Retriever = acquire information
Analyzer  = understand and structure information
Writer    = present information

This makes the system easier to test, modify, and reason about.

Why sequential execution?

The agents have data dependencies:

Retriever output -> Analyzer input
Analyzer output  -> Writer input

Therefore these stages cannot safely run independently.

Why asyncio?

The system performs I/O-bound operations such as LLM API calls.

Using asynchronous Python allows the application to avoid blocking the server while waiting for these operations.

Why custom orchestration?

The assignment explicitly requires understanding and implementing agent orchestration rather than hiding the workflow behind a framework.

Therefore the orchestration logic is implemented directly with Python and asyncio.

Current Limitations

The current Retriever Agent uses controlled demo source data rather than a production web-search system.

This was intentionally kept simple so the core assignment requirements could be demonstrated reliably:

Multi-agent architecture
Async orchestration
LLM analysis
Retry handling
Timeout handling
Graceful degradation
SSE streaming
Automated tests

A production version could replace the Retriever Agent with a real search or document retrieval service.

Assignment Scope

This project focuses on the orchestration layer rather than production infrastructure.

The following are intentionally outside the current scope:

Authentication
Database persistence
Message queues
Production deployment
Distributed workers
Production web-search infrastructure