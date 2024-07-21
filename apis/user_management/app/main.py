from fastapi import FastAPI, HTTPException
from mangum import Mangum
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

@app.get("/")
def read_root():
    """Root endpoint to check API status.

    Returns:
        dict: Welcome message.
    """
    logger.info("Root endpoint called")
    return {"message": "Welcome to the User Management API"}

@app.get("/users/{user_id}")
def read_user(user_id: UUID):
    """Read a user by its ID.

    Args:
        user_id (UUID): ID of the user to read.

    Returns:
        dict: The user model.

    Raises:
        HTTPException: If the user is not found or if there is an error.
    """
    try:
        user = user_service.get_user(str(user_id))
        if user:
            logger.info(f"User {user_id} retrieved successfully")
            return user
        logger.error(f"User {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    except ClientError as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Error getting user")
    except Exception as e:
        logger.error(f"Unexpected error getting user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

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

handler = Mangum(app)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
