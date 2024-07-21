from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class UserCreate(BaseModel):
    user_id: str
    name: str
    joined_at: int

class UserUpdate(BaseModel):
    name: Optional[str]
