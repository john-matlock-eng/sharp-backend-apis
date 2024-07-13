from fastapi import FastAPI, HTTPException
from mangum import Mangum
from app.services.user_service import UserService
from app.lib.dynamodb_controller import DynamoDBController
import os
import logging
from botocore.exceptions import ClientError

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize DynamoDB controller and user service
table_name = os.getenv('TABLE_NAME', 'sharp_app_data')
dynamodb_controller = DynamoDBController(table_name)
user_service = UserService(dynamodb_controller)

@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"message": "Welcome to the User Management API"}

@app.get("/users/{user_id}")
def read_user(user_id: int):
    try:
        user = user_service.get_user(user_id)
        if user:
            logger.info(f"User {user_id} retrieved successfully")
            return user
        logger.error(f"User {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    except ClientError as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Error getting user")

@app.post("/users/")
def create_user(user_id: int, name: str):
    try:
        existing_user = user_service.get_user(user_id)
        if existing_user:
            logger.error(f"User ID {user_id} already exists")
            raise HTTPException(status_code=400, detail="User ID already exists")
        user_service.create_user(user_id, name)
        logger.info(f"User {user_id} created successfully")
        return {"message": "User created successfully"}
    except ClientError as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Error creating user")

@app.put("/users/{user_id}")
def update_user(user_id: int, name: str = None):
    try:
        user = user_service.get_user(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        user_service.update_user(user_id, name)
        logger.info(f"User {user_id} updated successfully")
        return {"message": "User updated successfully"}
    except ClientError as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Error updating user")

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    try:
        user = user_service.get_user(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        user_service.delete_user(user_id)
        logger.info(f"User {user_id} deleted successfully")
        return {"message": "User deleted successfully"}
    except ClientError as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail="Error deleting user")

# Create a handler for AWS Lambda
handler = Mangum(app)
