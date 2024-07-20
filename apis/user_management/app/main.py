from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from mangum import Mangum
from pydantic import UUID4
import os
import logging
from botocore.exceptions import ClientError
from app.services.user_service import UserService
from app.lib.dynamodb_controller import DynamoDBController
from app.models.user_schema import UserCreate, UserUpdate

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DynamoDB controller and user service
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
def read_user(user_id: UUID4):
    """Read a user by its ID.

    Args:
        user_id (UUID4): ID of the user to read.

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

@app.post("/users/")
def create_user(user: UserCreate):
    """Create a new user.

    Args:
        user (UserCreate): User creation data.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If there is an error creating the user.
    """
    try:
        existing_user = user_service.get_user(str(user.user_id))
        if existing_user:
            logger.error(f"User ID {user.user_id} already exists")
            raise HTTPException(status_code=400, detail="User ID already exists")
        user_service.create_user(user)
        logger.info(f"User {user.user_id} created successfully")
        return {"message": "User created successfully"}
    except ClientError as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Error creating user")
    except Exception as e:
        logger.error(f"Unexpected error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/users/{user_id}")
def update_user(user_id: UUID4, user: UserUpdate):
    """Update a user by its ID.

    Args:
        user_id (UUID4): ID of the user to update.
        user (UserUpdate): User update data.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If the user is not found or if there is an error updating the user.
    """
    try:
        existing_user = user_service.get_user(str(user_id))
        if not existing_user:
            logger.error(f"User {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        user_service.update_user(str(user_id), user)
        logger.info(f"User {user_id} updated successfully")
        return {"message": "User updated successfully"}
    except ClientError as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Error updating user")
    except Exception as e:
        logger.error(f"Unexpected error updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/users/{user_id}")
def delete_user(user_id: UUID4):
    """Delete a user by its ID.

    Args:
        user_id (UUID4): ID of the user to delete.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If the user is not found or if there is an error deleting the user.
    """
    try:
        existing_user = user_service.get_user(str(user_id))
        if not existing_user:
            logger.error(f"User {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        user_service.delete_user(str(user_id))
        logger.info(f"User {user_id} deleted successfully")
        return {"message": "User deleted successfully"}
    except ClientError as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail="Error deleting user")
    except Exception as e:
        logger.error(f"Unexpected error deleting user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

handler = Mangum(app)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
