from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import UUID4
import os
import logging
from mangum import Mangum
from app.services.quiz_service import QuizService
from app.services.community_service import CommunityService, requires_member, requires_quiz_owner
from app.services.cognito_service import get_current_user
from app.lib.dynamodb_controller import DynamoDBController
from app.models.quiz_schema import QuizCreate, QuizUpdate
from app.models.question_schema import QuestionModel

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="https://your_cognito_domain/oauth2/token")

app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DynamoDB controller and services
table_name = os.getenv('TABLE_NAME', 'sharp_app_data')
dynamodb_controller = DynamoDBController(table_name)
quiz_service = QuizService(dynamodb_controller)
community_service = CommunityService(dynamodb_controller)

@app.post("/community/{community_id}/quizzes/")
@requires_member('community_id')
async def create_quiz(quiz_data: QuizCreate, current_user: dict = Depends(get_current_user), community_id: str = None):
    logger.info(f"Creating quiz for community {community_id}")
    quiz_data.owner_ids = [current_user["sub"]]
    await quiz_service.create_quiz(quiz_data)
    return {"message": "Quiz created successfully"}

@app.get("/quizzes/{quiz_id}")
@requires_member('community_id')
async def get_quiz(quiz_id: UUID4, current_user: dict = Depends(get_current_user)):
    quiz_metadata = await quiz_service.get_quiz_metadata(str(quiz_id))
    if not quiz_metadata:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    community_id = quiz_metadata['community_id']
    questions, _ = await quiz_service.get_questions_by_quiz_id(community_id, str(quiz_id))
    return {"metadata": quiz_metadata, "questions": questions}

@app.get("/quizzes/")
async def list_quizzes(
    community_id: str,
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, description="Number of quizzes to return"),
    last_evaluated_key: str = Query(None, description="Token for pagination")
):
    quizzes, next_token = await quiz_service.list_quizzes(community_id, limit, last_evaluated_key)
    return {"quizzes": quizzes, "next_token": next_token}

@app.put("/quizzes/{quiz_id}")
@requires_quiz_owner('quiz_id')
async def update_quiz(quiz_id: UUID4, quiz_data: QuizUpdate, current_user: dict = Depends(get_current_user)):
    quiz_metadata = await quiz_service.get_quiz_metadata(str(quiz_id))
    if not quiz_metadata:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    await quiz_service.update_quiz(quiz_id, quiz_data)
    return {"message": "Quiz updated successfully"}

@app.delete("/quizzes/{quiz_id}")
@requires_quiz_owner('quiz_id')
async def delete_quiz(quiz_id: UUID4, current_user: dict = Depends(get_current_user)):
    quiz_metadata = await quiz_service.get_quiz_metadata(str(quiz_id))
    if not quiz_metadata:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    await quiz_service.delete_quiz(str(quiz_id))
    return {"message": "Quiz deleted successfully"}

@app.post("/quizzes/{quiz_id}/questions/")
@requires_quiz_owner('quiz_id')
async def create_question(quiz_id: UUID4, question_data: QuestionModel, current_user: dict = Depends(get_current_user)):
    quiz_metadata = await quiz_service.get_quiz_metadata(str(quiz_id))
    if not quiz_metadata:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    await quiz_service.create_question(quiz_metadata['community_id'], str(quiz_id), question_data)
    return {"message": "Question created successfully"}

@app.get("/quizzes/{quiz_id}/questions/{question_id}")
@requires_member('community_id')
async def get_question(quiz_id: UUID4, question_id: UUID4, current_user: dict = Depends(get_current_user)):
    quiz_metadata = await quiz_service.get_quiz_metadata(str(quiz_id))
    if not quiz_metadata:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    question = await quiz_service.get_question(quiz_metadata['community_id'], str(quiz_id), str(question_id))
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return question

@app.put("/quizzes/{quiz_id}/questions/{question_id}")
@requires_quiz_owner('quiz_id')
async def update_question(quiz_id: UUID4, question_id: UUID4, question_data: QuestionModel, current_user: dict = Depends(get_current_user)):
    quiz_metadata = await quiz_service.get_quiz_metadata(str(quiz_id))
    if not quiz_metadata:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    await quiz_service.update_question(quiz_metadata['community_id'], str(quiz_id), str(question_id), question_data)
    return {"message": "Question updated successfully"}

@app.delete("/quizzes/{quiz_id}/questions/{question_id}")
@requires_quiz_owner('quiz_id')
async def delete_question(quiz_id: UUID4, question_id: UUID4, current_user: dict = Depends(get_current_user)):
    quiz_metadata = await quiz_service.get_quiz_metadata(str(quiz_id))
    if not quiz_metadata:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    await quiz_service.delete_question(quiz_metadata['community_id'], str(quiz_id), str(question_id))
    return {"message": "Question deleted successfully"}

@app.get("/quizzes/{quiz_id}/questions")
@requires_member('community_id')
async def get_quiz_questions(
    quiz_id: UUID4,
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, description="Number of questions to return"),
    last_evaluated_key: str = Query(None, description="Token for pagination")
):
    quiz_metadata = await quiz_service.get_quiz_metadata(str(quiz_id))
    if not quiz_metadata:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    questions, next_token = await quiz_service.get_questions_by_quiz_id(quiz_metadata['community_id'], str(quiz_id), limit, last_evaluated_key)
    return {"questions": questions, "next_token": next_token}

handler = Mangum(app)
