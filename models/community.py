from pydantic import BaseModel

class CommunityCreate(BaseModel):
    community_id: int
    name: str

class CommunityUpdate(BaseModel):
    name: str = None
