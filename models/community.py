from pydantic import BaseModel, UUID4

class CommunityCreate(BaseModel):
    community_id: UUID4
    name: str

class CommunityUpdate(BaseModel):
    name: str = None
