from pydantic import BaseModel, UUID4, Field
from typing import List, Optional

class Question(BaseModel):
    question_id: str
    question_text: str
    options: List[str]
    answer: List[str]

class QuizBase(BaseModel):
    community_id: UUID4
    title: str
    description: Optional[str] = None

class QuizCreate(QuizBase):
    quiz_id: str = Field(..., description="Unique identifier for the quiz")
    owner_ids: List[str] = Optional[Field(..., description="List of user IDs who own the quiz")]
    title: str = Field(..., description="Title of the quiz")
    description: Optional[str] = Field(None, description="Description of the quiz")

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    owner_ids: Optional[List[str]] = None
