from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import UUID4
import os
import logging
from botocore.exceptions import ClientError
from app.services.quiz_service import QuizService
from app.services.community_service import CommunityService
from app.services.cognito_service import get_current_user
from app.lib.dynamodb_controller import DynamoDBController
from app.models.quiz_schema import QuizCreate, QuizUpdate

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

@app.get("/quizzes/{community_id}")
def list_quizzes(community_id: UUID4, current_user: dict = Depends(get_current_user)):
    try:
        logger.info(f"Received request to list quizzes for community ID: {community_id}")
        quizzes = quiz_service.list_quizzes(str(community_id))
        logger.info("Quizzes listed successfully")
        return {"quizzes": quizzes}
    except ClientError as e:
        logger.error(f"Error listing quizzes: {e}")
        raise HTTPException(status_code=500, detail="Error listing quizzes")
    except Exception as e:
        logger.error(f"Unexpected error listing quizzes: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/quizzes/{community_id}/{quiz_id}")
def read_quiz(community_id: UUID4, quiz_id: UUID4, current_user: dict = Depends(get_current_user)):
    try:
        logger.info(f"Received request to read quiz with ID: {quiz_id} in community {community_id}")
        quiz = quiz_service.get_quiz(str(community_id), str(quiz_id))
        if quiz:
            logger.info(f"Quiz {quiz_id} retrieved successfully")
            return quiz
        logger.error(f"Quiz {quiz_id} not found")
        raise HTTPException(status_code=404, detail="Quiz not found")
    except ClientError as e:
        logger.error(f"Error getting quiz: {e}")
        raise HTTPException(status_code=500, detail="Error getting quiz")
    except Exception as e:
        logger.error(f"Unexpected error getting quiz: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/quizzes/")
def create_quiz(quiz: QuizCreate, current_user: dict = Depends(get_current_user)):
    try:
        logger.info(f"Received request to create quiz with ID: {quiz.quiz_id}")

        # Authorization check using CommunityService
        community_service.assert_user_is_owner(str(quiz.community_id), current_user["sub"])

        existing_quiz = quiz_service.get_quiz(str(quiz.community_id), str(quiz.quiz_id))
        if existing_quiz:
            logger.error(f"Quiz ID {quiz.quiz_id} already exists")
            raise HTTPException(status_code=400, detail="Quiz ID already exists")

        quiz_service.create_quiz(quiz)
        logger.info(f"Quiz {quiz.quiz_id} created successfully")
        return {"message": "Quiz created successfully"}
    except ClientError as e:
        logger.error(f"Error creating quiz: {e}")
        raise HTTPException(status_code=500, detail="Error creating quiz")
    except Exception as e:
        logger.error(f"Unexpected error creating quiz: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/quizzes/{community_id}/{quiz_id}")
def update_quiz(community_id: UUID4, quiz_id: UUID4, quiz: QuizUpdate, current_user: dict = Depends(get_current_user)):
    try:
        logger.info(f"Received request to update quiz with ID: {quiz_id}")

        # Authorization check using CommunityService
        community_service.assert_user_is_owner(str(community_id), current_user["sub"])

        existing_quiz = quiz_service.get_quiz(str(community_id), str(quiz_id))
        if not existing_quiz:
            logger.error(f"Quiz {quiz_id} not found")
            raise HTTPException(status_code=404, detail="Quiz not found")

        quiz_service.update_quiz(str(community_id), str(quiz_id), quiz.dict(exclude_unset=True))
        logger.info(f"Quiz {quiz_id} updated successfully")
        return {"message": "Quiz updated successfully"}
    except ClientError as e:
        logger.error(f"Error updating quiz: {e}")
        raise HTTPException(status_code=500, detail="Error updating quiz")
    except Exception as e:
        logger.error(f"Unexpected error updating quiz: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/quizzes/{community_id}/{quiz_id}")
def delete_quiz(community_id: UUID4, quiz_id: UUID4, current_user: dict = Depends(get_current_user)):
    try:
        logger.info(f"Received request to delete quiz with ID: {quiz_id}")

        # Authorization check using CommunityService
        community_service.assert_user_is_owner(str(community_id), current_user["sub"])

        quiz = quiz_service.get_quiz(str(community_id), str(quiz_id))
        if not quiz:
            logger.error(f"Quiz {quiz_id} not found")
            raise HTTPException(status_code=404, detail="Quiz not found")
        quiz_service.delete_quiz(str(community_id), str(quiz_id))
        logger.info(f"Quiz {quiz_id} deleted successfully")
        return {"message": "Quiz deleted successfully"}
    except ClientError as e:
        logger.error(f"Error deleting quiz: {e}")
        raise HTTPException(status_code=500, detail="Error deleting quiz")
    except Exception as e:
        logger.error(f"Unexpected error deleting quiz: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
