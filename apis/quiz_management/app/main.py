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
def create_quiz(
    quiz_data: QuizCreate, 
    current_user: dict = Depends(get_current_user), 
    community_id: str = None, 
    quiz_service: QuizService = Depends(lambda: quiz_service)
):
    logger.info(f"Creating quiz for community {community_id}")
    quiz_data.owner_ids = [current_user["sub"]]
    quiz_service.create_quiz(quiz_data)
    return {"message": "Quiz created successfully"}

@app.get("/community/{community_id}/quizzes/{quiz_id}")
@requires_member('community_id')
def get_quiz(
    quiz_id: UUID4, 
    current_user: dict = Depends(get_current_user),
    community_id: str = None, 
    quiz_service: QuizService = Depends(lambda: quiz_service)
):
    quiz_metadata = quiz_service.get_quiz_metadata(str(community_id), str(quiz_id))
    print(quiz_metadata)
    if not quiz_metadata:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    questions, _ = quiz_service.get_questions_by_quiz_id(community_id, str(quiz_id))
    return {"metadata": quiz_metadata, "questions": questions}

@app.get("/community/{community_id}/quizzes/")
@requires_member('community_id')
def list_quizzes(
    community_id: str,
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, description="Number of quizzes to return"),
    last_evaluated_key: str = Query(None, description="Token for pagination"),
    quiz_service: QuizService = Depends(lambda: quiz_service)
):
    quizzes, next_token = quiz_service.list_quizzes(community_id, limit, last_evaluated_key)
    return {"quizzes": quizzes, "next_token": next_token}

@app.put("/community/{community_id}/quizzes/{quiz_id}")
@requires_quiz_owner("community_id", 'quiz_id')
def update_quiz(
    community_id: str,
    quiz_id: UUID4, 
    quiz_data: QuizUpdate, 
    current_user: dict = Depends(get_current_user), 
    quiz_service: QuizService = Depends(lambda: quiz_service)
):
    quiz_metadata = quiz_service.get_quiz_metadata(str(community_id), str(quiz_id))
    if not quiz_metadata:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz_service.update_quiz(quiz_id, quiz_data)
    return {"message": "Quiz updated successfully"}

@app.delete("/community/{community_id}/quizzes/{quiz_id}")
@requires_quiz_owner("community_id", 'quiz_id')
def delete_quiz(
    community_id: str,
    quiz_id: UUID4, 
    current_user: dict = Depends(get_current_user), 
    quiz_service: QuizService = Depends(lambda: quiz_service)
):
    quiz_metadata = quiz_service.get_quiz_metadata(str(community_id), str(quiz_id))
    if not quiz_metadata:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz_service.delete_quiz(str(community_id), str(quiz_id))
    return {"message": "Quiz deleted successfully"}

@app.post("/community/{community_id}/quizzes/{quiz_id}/questions/")
@requires_quiz_owner("community_id", 'quiz_id')
def create_question(
    community_id: UUID4, 
    quiz_id: UUID4, 
    question_data: QuestionModel, 
    current_user: dict = Depends(get_current_user), 
    quiz_service: QuizService = Depends(lambda: quiz_service)
):
    quiz_metadata = quiz_service.get_quiz_metadata(str(community_id), str(quiz_id))
    if not quiz_metadata:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz_service.create_question(str(community_id), str(quiz_id), question_data)
    return {"message": "Question created successfully"}

@app.get("/community/{community_id}/quizzes/{quiz_id}/questions/{question_id}")
@requires_member('community_id')
def get_question(
    community_id: UUID4,
    quiz_id: UUID4, 
    question_id: UUID4, 
    current_user: dict = Depends(get_current_user), 
    quiz_service: QuizService = Depends(lambda: quiz_service)
):
    quiz_metadata = quiz_service.get_quiz_metadata(str(community_id), str(quiz_id))
    if not quiz_metadata:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    question = quiz_service.get_question(str(community_id), str(quiz_id), str(question_id))
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return question

@app.put("/community/{community_id}/quizzes/{quiz_id}/questions/{question_id}")
@requires_quiz_owner("community_id", 'quiz_id')
def update_question(
    community_id: UUID4,
    quiz_id: UUID4, 
    question_id: UUID4, 
    question_data: QuestionModel, 
    current_user: dict = Depends(get_current_user), 
    quiz_service: QuizService = Depends(lambda: quiz_service)
):
    quiz_metadata = quiz_service.get_quiz_metadata(str(community_id), str(quiz_id))
    if not quiz_metadata:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz_service.update_question(str(community_id), str(quiz_id), str(question_id), question_data)
    return {"message": "Question updated successfully"}

@app.delete("/community/{community_id}/quizzes/{quiz_id}/questions/{question_id}")
@requires_quiz_owner("community_id", 'quiz_id')
def delete_question(
    community_id: UUID4,
    quiz_id: UUID4, 
    question_id: UUID4, 
    current_user: dict = Depends(get_current_user), 
    quiz_service: QuizService = Depends(lambda: quiz_service)
):
    quiz_metadata = quiz_service.get_quiz_metadata(str(community_id), str(quiz_id))
    if not quiz_metadata:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz_service.delete_question(str(community_id), str(quiz_id), str(question_id))
    return {"message": "Question deleted successfully"}

@app.get("/community/{community_id}/quizzes/{quiz_id}/questions")
@requires_member('community_id')
def get_quiz_questions(
    community_id: UUID4,
    quiz_id: UUID4,
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, description="Number of questions to return"),
    last_evaluated_key: str = Query(None, description="Token for pagination"),
    quiz_service: QuizService = Depends(lambda: quiz_service)
):
    quiz_metadata = quiz_service.get_quiz_metadata(str(community_id), str(quiz_id))
    if not quiz_metadata:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    questions, next_token = quiz_service.get_questions_by_quiz_id(str(community_id), str(quiz_id), limit, last_evaluated_key)
    return {"questions": questions, "next_token": next_token}

handler = Mangum(app)
