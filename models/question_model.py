from pydantic import BaseModel, UUID4
from typing import List, Optional

class QuestionBase(BaseModel):
    question_text: str
    options: List[str]
    answer: List[str]

class QuestionCreate(QuestionBase):
    question_id: UUID4
    quiz_id: UUID4
    community_id: UUID4
    options: List[str]
    answer: List[str]
    question_text: str
    question_type: str

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    options: Optional[List[str]] = None
    answer: Optional[List[str]] = None

class QuestionInDB(QuestionBase):
    question_id: UUID4
    quiz_id: UUID4
    community_id: UUID4
