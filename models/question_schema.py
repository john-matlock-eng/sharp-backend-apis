from pydantic import BaseModel, UUID4
from typing import List

class QuestionModel(BaseModel):
    question_id: UUID4
    quiz_id: UUID4
    community_id: UUID4
    question_text: str
    options: List[str]
    answer: List[str]
