import asyncio
from collections.abc import AsyncGenerator

from app.agents.retriever import RetrieverAgent
from app.agents.analyzer import AnalyzerAgent
from app.agents.writer import WriterAgent


class TaskOrchestrator:
    """
    Coordinates the three specialized agents.

    Flow:
        Retriever -> Analyzer -> Writer

    Reliability:
        - timeout
        - retry
        - graceful fallback
        - SSE progress events
    """

    def __init__(self):

        self.retriever = RetrieverAgent()
        self.analyzer = AnalyzerAgent()
        self.writer = WriterAgent()

    # ---------------------------------------------------------
    # RETRY + TIMEOUT
    # ---------------------------------------------------------

    async def _run_with_retry(
        self,
        operation,
        retries: int = 2,
        timeout: float = 15.0,
    ):
        """
        Execute an async operation with timeout and retry support.
        """

        last_error = None

        for attempt in range(retries + 1):

            try:

                print(
                    f"[Orchestrator] Attempt "
                    f"{attempt + 1}/{retries + 1}"
                )

                result = await asyncio.wait_for(
                    operation(),
                    timeout=timeout,
                )

                print("[Orchestrator] Operation succeeded")

                return result

            except Exception as error:

                last_error = error

                print(
                    f"[Orchestrator] Attempt "
                    f"{attempt + 1} failed: "
                    f"{type(error).__name__}: {error}"
                )

                if attempt < retries:

                    print("[Orchestrator] Retrying...")

                    await asyncio.sleep(1)

        raise last_error

    # ---------------------------------------------------------
    # NORMAL EXECUTION
    # ---------------------------------------------------------

    async def run(
        self,
        company: str,
        question: str,
    ):

        # -------------------------
        # 1. Retriever
        # -------------------------

        print("[Orchestrator] Starting Retriever")

        sources = await self._run_with_retry(
            lambda: self.retriever.retrieve(
                company,
                question,
            )
        )

        print(
            f"[Orchestrator] Retrieved {len(sources)} sources"
        )

        # -------------------------
        # 2. Analyzer
        # -------------------------

        print("[Orchestrator] Starting Analyzer")

        try:

            analysis = await self._run_with_retry(
                lambda: self.analyzer.analyze(
                    company,
                    question,
                    sources,
                )
            )

        except Exception as error:

            print(
                "[Orchestrator] Analyzer failed: "
                f"{type(error).__name__}: {error}"
            )

            analysis = {
                "summary": (
                    "Analysis could not be completed "
                    "because the analysis service failed."
                ),
                "key_facts": [],
                "important_points": [],
                "error": str(error),
            }

        # -------------------------
        # 3. Writer
        # -------------------------

        print("[Orchestrator] Starting Writer")

        if isinstance(analysis, dict):

            answer = (
                f"Company: {company}\n\n"
                f"Question: {question}\n\n"
                f"Summary:\n"
                f"{analysis['summary']}"
            )

        else:

            try:

                answer = await self._run_with_retry(
                    lambda: self.writer.write(
                        company,
                        question,
                        analysis,
                    )
                )

            except Exception as error:

                print(
                    "[Orchestrator] Writer failed: "
                    f"{type(error).__name__}: {error}"
                )

                answer = (
                    f"Company: {company}\n\n"
                    f"Question: {question}\n\n"
                    f"Summary:\n"
                    f"{analysis.summary}\n\n"
                    f"Writer service failed."
                )

        print("[Orchestrator] Task completed")

        return {
            "company": company,
            "question": question,
            "sources": sources,
            "analysis": analysis,
            "answer": answer,
        }

    # ---------------------------------------------------------
    # SSE STREAM
    # ---------------------------------------------------------

    async def stream(
        self,
        company: str,
        question: str,
    ) -> AsyncGenerator[dict, None]:

        try:

            # =================================================
            # RETRIEVER
            # =================================================

            yield {
                "agent": "retriever",
                "status": "started",
                "message": "Retrieving source material",
            }

            print("[SSE] Retriever started")

            try:

                sources = await self._run_with_retry(
                    lambda: self.retriever.retrieve(
                        company,
                        question,
                    )
                )

            except Exception as error:

                print(
                    "[SSE] Retriever failed: "
                    f"{type(error).__name__}: {error}"
                )

                yield {
                    "agent": "retriever",
                    "status": "failed",
                    "message": (
                        "Retriever failed. "
                        "Unable to continue."
                    ),
                    "error": str(error),
                }

                return

            yield {
                "agent": "retriever",
                "status": "completed",
                "message": (
                    f"Retrieved {len(sources)} sources"
                ),
            }

            print("[SSE] Retriever completed")

            # =================================================
            # ANALYZER
            # =================================================

            yield {
                "agent": "analyzer",
                "status": "started",
                "message": "Analyzing source material",
            }

            print("[SSE] Analyzer started")

            try:

                analysis = await self._run_with_retry(
                    lambda: self.analyzer.analyze(
                        company,
                        question,
                        sources,
                    )
                )

                analyzer_failed = False

            except Exception as error:

                print(
                    "[SSE] Analyzer failed: "
                    f"{type(error).__name__}: {error}"
                )

                analyzer_failed = True

                analysis = {
                    "summary": (
                        "Analysis could not be completed."
                    ),
                    "key_facts": [],
                    "important_points": [],
                    "error": str(error),
                }

                yield {
                    "agent": "analyzer",
                    "status": "failed",
                    "message": (
                        "Analyzer failed; "
                        "using fallback response"
                    ),
                    "error": str(error),
                }

            if not analyzer_failed:

                yield {
                    "agent": "analyzer",
                    "status": "completed",
                    "message": "Analysis completed",
                }

                print("[SSE] Analyzer completed")

            # =================================================
            # WRITER
            # =================================================

            yield {
                "agent": "writer",
                "status": "started",
                "message": "Generating final response",
            }

            print("[SSE] Writer started")

            if isinstance(analysis, dict):

                answer = (
                    f"Company: {company}\n\n"
                    f"Question: {question}\n\n"
                    f"Summary:\n"
                    f"{analysis['summary']}"
                )

            else:

                try:

                    answer = await self._run_with_retry(
                        lambda: self.writer.write(
                            company,
                            question,
                            analysis,
                        )
                    )

                except Exception as error:

                    print(
                        "[SSE] Writer failed: "
                        f"{type(error).__name__}: {error}"
                    )

                    answer = (
                        f"Company: {company}\n\n"
                        f"Question: {question}\n\n"
                        f"Summary:\n"
                        f"{analysis.summary}\n\n"
                        f"Writer service failed."
                    )

                    yield {
                        "agent": "writer",
                        "status": "failed",
                        "message": (
                            "Writer failed; "
                            "using fallback response"
                        ),
                        "error": str(error),
                    }

            yield {
                "agent": "writer",
                "status": "completed",
                "message": "Final response generated",
                "answer": answer,
            }

            print("[SSE] Writer completed")

            # =================================================
            # COMPLETE
            # =================================================

            yield {
                "agent": "orchestrator",
                "status": "completed",
                "message": "Task completed successfully",
            }

            print("[SSE] Task completed")

        except Exception as error:

            # -------------------------------------------------
            # LAST SAFETY NET
            # -------------------------------------------------

            print(
                "[SSE] UNEXPECTED ERROR: "
                f"{type(error).__name__}: {error}"
            )

            yield {
                "agent": "orchestrator",
                "status": "failed",
                "message": "Unexpected orchestration error",
                "error": str(error),
            }