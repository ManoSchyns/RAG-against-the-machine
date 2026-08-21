from pydantic import BaseModel, Field
import uuid
from typing import List


class MinimalSource(BaseModel):
    """Represents a source location within an ingested file."""

    file_path: str
    first_character_index: int
    last_character_index: int
    content: str = Field(default="None")


class UnansweredQuestion(BaseModel):
    """Represents a question that has not yet been answered."""

    question_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())
    )
    question: str


class AnsweredQuestion(UnansweredQuestion):
    """Represents a question together with its answer and sources."""

    sources: List[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    """Represents a dataset containing answered and unanswered questions."""

    rag_questions: List[AnsweredQuestion | UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    """Represents the sources retrieved for a question."""

    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    """Represents search results together with the generated answer."""

    answer: str


class StudentSearchResults(BaseModel):
    """Represents the results of a search operation."""

    search_results: List[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(BaseModel):
    """Represents search results together with generated answers."""

    search_results: List[MinimalAnswer]
    k: int
