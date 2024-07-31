from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID

class QuestionModel(BaseModel):
    questionText: str
    options: List[str]
    answer: List[str]

class QuizCreate(BaseModel):
    quiz_id: UUID
    community_id: UUID
    topic: str
    description: str
    questions: List[QuestionModel]
    created_at: int = Field(default_factory=lambda: int(datetime.now(timezone.utc).timestamp()))

class QuizUpdate(BaseModel):
    topic: Optional[str]
    description: Optional[str]
    questions: Optional[List[QuestionModel]]
