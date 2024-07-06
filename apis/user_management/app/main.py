from fastapi import FastAPI, HTTPException
from mangum import Mangum

app = FastAPI()

# Simulate a database with an in-memory dictionary
users_db = {
    1: {"name": "John Doe", "email": "john.doe@example.com"},
    2: {"name": "Jane Doe", "email": "jane.doe@example.com"}
}

@app.get("/")
def read_root():
    return {"message": "Welcome to the User Management API"}

@app.get("/users/{user_id}")
def read_user(user_id: int):
    user = users_db.get(user_id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/users/")
def create_user(user_id: int, name: str, email: str):
    if user_id in users_db:
        raise HTTPException(status_code=400, detail="User ID already exists")
    users_db[user_id] = {"name": name, "email": email}
    return users_db[user_id]

@app.put("/users/{user_id}")
def update_user(user_id: int, name: str = None, email: str = None):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if name:
        user["name"] = name
    if email:
        user["email"] = email
    users_db[user_id] = user
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del users_db[user_id]
    return {"detail": "User deleted"}

# Create a handler for AWS Lambda
handler = Mangum(app)
