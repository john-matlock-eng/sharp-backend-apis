from pydantic import BaseModel, UUID4, Field
from typing import List, Optional

class Question(BaseModel):
    question_id: str
    text: str
    options: List[str]
    answer: str

class QuizBase(BaseModel):
    community_id: UUID4
    title: str
    description: Optional[str] = None
    questions: List[Question]

class QuizCreate(QuizBase):
    quiz_id: str = Field(..., description="Unique identifier for the quiz")

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    questions: Optional[List[Question]] = None
