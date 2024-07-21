from fastapi import FastAPI, HTTPException
from app.services.user_service import UserService
from app.lib.dynamodb_controller import DynamoDBController
from app.models.user_schema import UserCreate, UserUpdate
import os
import logging
from uuid import UUID

app = FastAPI()
logger = logging.getLogger(__name__)

table_name = os.getenv('TABLE_NAME', 'sharp_app_data')
dynamodb_controller = DynamoDBController(table_name)
user_service = UserService(dynamodb_controller)

@app.post("/users/")
def create_user(user: UserCreate):
    try:
        existing_user = user_service.get_user(str(user.user_id))
        if existing_user:
            logger.error(f"User ID {user.user_id} already exists")
            raise HTTPException(status_code=400, detail="User ID already exists")
        user_service.create_user(user)
        logger.info(f"User {user.user_id} created successfully")
        return {"message": "User created successfully"}
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Error creating user")

@app.get("/users/{user_id}")
def read_user(user_id: UUID):
    try:
        user = user_service.get_user(str(user_id))
        if user:
            logger.info(f"User {user_id} retrieved successfully")
            return user
        logger.error(f"User {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Error getting user")

@app.put("/users/{user_id}")
def update_user(user_id: UUID, user: UserUpdate):
    try:
        existing_user = user_service.get_user(str(user_id))
        if not existing_user:
            logger.error(f"User {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        user_service.update_user(str(user_id), user)
        logger.info(f"User {user_id} updated successfully")
        return {"message": "User updated successfully"}
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Error updating user")

@app.delete("/users/{user_id}")
def delete_user(user_id: UUID):
    try:
        existing_user = user_service.get_user(str(user_id))
        if not existing_user:
            logger.error(f"User {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        user_service.delete_user(str(user_id))
        logger.info(f"User {user_id} deleted successfully")
        return {"message": "User deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail="Error deleting user")

@app.get("/users/{user_id}/communities")
def list_user_communities(user_id: UUID):
    try:
        communities = user_service.list_communities_for_user(str(user_id))
        logger.info(f"Communities for user {user_id} retrieved successfully")
        return communities
    except Exception as e:
        logger.error(f"Error listing communities for user: {e}")
        raise HTTPException(status_code=500, detail="Error listing communities for user")
