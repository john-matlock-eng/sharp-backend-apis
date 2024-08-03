from pydantic import BaseModel, UUID4
from typing import List, Optional

class QuestionModel(BaseModel):
    question_id: UUID4
    question_text: str
    options: List[str]
    answer: List[str]

class QuizMetadataModel(BaseModel):
    quiz_id: UUID4
    community_id: UUID4
    topic: str
    description: Optional[str]
    created_at: int

class QuizCreateModel(BaseModel):
    metadata: QuizMetadataModel
    questions: List[QuestionModel]

class QuizUpdateModel(BaseModel):
    metadata: Optional[QuizMetadataModel]
    questions: Optional[List[QuestionModel]]
