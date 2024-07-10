from fastapi import FastAPI, HTTPException
from mangum import Mangum
from app.user_service import UserService
import os

app = FastAPI()

# Initialize DynamoDB controller and user service
table_name = os.getenv('TABLE_NAME', 'sharp_app_data')
dynamodb_controller = DynamoDBController(table_name)
user_service = UserService(dynamodb_controller)

@app.get("/")
def read_root():
    return {"message": "Welcome to the User Management API"}

@app.get("/users/{user_id}")
def read_user(user_id: int):
    user = user_service.get_user(user_id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/users/")
def create_user(user_id: int, name: str):
    existing_user = user_service.get_user(user_id)
    if existing_user:
        raise HTTPException(status_code=400, detail="User ID already exists")
    user_service.create_user(user_id, name)
    return {"message": "User created successfully"}

@app.put("/users/{user_id}")
def update_user(user_id: int, name: str = None):
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_service.update_user(user_id, name)
    return {"message": "User updated successfully"}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_service.delete_user(user_id)
    return {"message": "User deleted successfully"}

# Create a handler for AWS Lambda
handler = Mangum(app)
