from pydantic import BaseModel, UUID4

class UserCreate(BaseModel):
    user_id: UUID4
    moniker: str

class UserUpdate(BaseModel):
    moniker: str
