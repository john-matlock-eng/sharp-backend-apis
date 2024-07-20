from pydantic import BaseModel
from uuid import UUID

class UserCreate(BaseModel):
    user_id: UUID
    moniker: str

class UserUpdate(BaseModel):
    moniker: str
