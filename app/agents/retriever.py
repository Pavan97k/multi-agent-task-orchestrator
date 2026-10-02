from app.models import Source


class RetrieverAgent:
    """
    Retrieves source material related to a company and question.
    """

    async def retrieve(self, company: str, question: str) -> list[Source]:

        sources = [
            Source(
                title=f"{company} - Company Overview",
                url="https://example.com/company-overview",
                content=(
                    f"{company} is a technology company. "
                    f"The user is asking about: {question}."
                ),
            ),
            Source(
                title=f"{company} - Artificial Intelligence",
                url="https://example.com/artificial-intelligence",
                content=(
                    f"{company} develops and invests in artificial "
                    f"intelligence technologies and AI-powered products."
                ),
            ),
        ]

        return sources