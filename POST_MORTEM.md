# Post-Mortem - Multi-Agent Task Orchestrator

## 1. Agent Boundaries

The system separates responsibilities into three agents:

- **Retriever Agent:** responsible for obtaining and returning source material.
- **Analyzer Agent:** responsible for extracting structured information from the sources using the LLM.
- **Writer Agent:** responsible for converting the structured analysis into a readable final response.

The clearest boundary is between retrieval and analysis. The Retriever provides source material, while the Analyzer determines what information is important.

The potentially unclear boundary is between the Analyzer and Writer. To avoid overlap, the Analyzer returns structured facts and points, while the Writer only handles final presentation and formatting.

---

## 2. What Would Break First at 100x the Current Load?

The external LLM API would likely become the first major bottleneck.

Each task currently depends on an asynchronous LLM request during the analysis stage. At significantly higher concurrency, API rate limits, latency, network failures, and available API quota would become important constraints.

The current retry and timeout mechanisms improve individual request reliability, but they do not provide distributed rate limiting, request queues, caching, or horizontal scaling.

A production version would therefore need bounded concurrency, rate limiting, caching, observability, and potentially distributed workers.

---

## 3. One Design Decision I Would Change

I would make the Retriever Agent configurable through a clear retrieval interface.

The current implementation uses controlled demo sources so the orchestration workflow remains deterministic. A production implementation should allow different retrieval providers to be plugged in without changing the Analyzer or Writer.

For example:

```text
Retriever Interface
       |
       +-- Demo Retriever
       |
       +-- Web Search Retriever
       |
       +-- Document Retriever

       ```

This would make the system easier to extend while keeping the agent boundaries intact.

---

## 4. One Unfinished Thing

The main unfinished part is production-grade information retrieval.

The current Retriever Agent uses controlled demonstration data rather than a live web-search or document-retrieval system. This was kept intentionally outside the core implementation so the assignment could focus on multi-agent orchestration, asynchronous execution, reliability handling, and SSE streaming.

A future version would replace the demo retriever with a real retrieval service while keeping the same agent interface.