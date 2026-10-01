from pydantic import BaseModel, ConfigDict, Field


class HealthOut(BaseModel):
    status: str


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # build directly from DocumentRecord

    id: str
    filename: str
    page_count: int
    chunk_count: int
    created_at: str


class DocumentStatsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_questions: int
    answered_count: int
    answer_rate: float | None
    average_top_score: float | None


class QueryIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)  # "   " fails min_length

    document_id: str = Field(min_length=1)
    question: str = Field(min_length=1, max_length=500)


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    page: int
    text: str
    score: float


class QueryOut(BaseModel):
    answer: str
    sources: list[SourceOut]
    top_score: float | None
    latency_ms: int
