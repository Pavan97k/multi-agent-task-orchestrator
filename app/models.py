from pydantic import BaseModel


class TaskRequest(BaseModel):
    company: str
    question: str


class Source(BaseModel):
    title: str
    url: str
    content: str


class AnalysisResult(BaseModel):
    summary: str
    key_facts: list[str]
    important_points: list[str]