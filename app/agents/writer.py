from app.models import AnalysisResult


class WriterAgent:
    """
    Writer Agent:
    Converts structured analysis into a concise final response.
    """

    async def write(
        self,
        company: str,
        question: str,
        analysis: AnalysisResult,
    ) -> str:

        answer = f"""
Company: {company}

Question: {question}

Summary:
{analysis.summary}

Key Facts:
"""

        for fact in analysis.key_facts:
            answer += f"- {fact}\n"

        answer += "\nImportant Points:\n"

        for point in analysis.important_points:
            answer += f"- {point}\n"

        return answer.strip()