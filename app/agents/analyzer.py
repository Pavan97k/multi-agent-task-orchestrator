import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import AsyncGroq

from app.models import AnalysisResult, Source


# Find the project root
# analyzer.py
#   -> agents
#   -> app
#   -> project root
BASE_DIR = Path(__file__).resolve().parents[2]

# Load .env from the project root
load_dotenv(BASE_DIR / ".env")


class AnalyzerAgent:
    """
    Analyzer Agent:
    Takes retrieved sources and extracts structured facts using an LLM.
    """

    def __init__(self):

        # Read the Groq API key
        api_key = os.getenv("GROQ_API_KEY")

        # Check whether API key exists
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not configured. Check the .env file."
            )

        # Create asynchronous Groq client
        self.client = AsyncGroq(
            api_key=api_key
        )

    async def analyze(
        self,
        company: str,
        question: str,
        sources: list[Source],
    ) -> AnalysisResult:

        # Convert sources into text
        source_text = "\n\n".join(
            f"Title: {source.title}\n"
            f"Content: {source.content}\n"
            f"URL: {source.url}"
            for source in sources
        )

        # Prompt for the Analyzer Agent
        prompt = f"""
You are an analysis agent.

Company: {company}

Question: {question}

Analyze ONLY the source material provided below.

SOURCE MATERIAL:
{source_text}

Return valid JSON with exactly these fields:

{{
    "summary": "short summary",
    "key_facts": [
        "fact 1",
        "fact 2"
    ],
    "important_points": [
        "point 1",
        "point 2"
    ]
}}

Do not invent facts that are not present in the sources.
"""

        # Call the Groq LLM asynchronously
        response = await self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You extract and structure factual "
                        "information from provided sources."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
        )

        # Get the LLM response
        content = response.choices[0].message.content.strip()

        # Remove Markdown code fences if the model adds them
        if content.startswith("```json"):
            content = content[7:]

        if content.startswith("```"):
            content = content[3:]

        if content.endswith("```"):
            content = content[:-3]

        # Remove any extra whitespace
        content = content.strip()

        # Convert JSON text into a Python dictionary
        data = json.loads(content)

        # Validate the result using Pydantic
        return AnalysisResult(**data)