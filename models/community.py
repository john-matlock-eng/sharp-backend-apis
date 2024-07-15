from pydantic import BaseModel, UUID4
from typing import List

class CommunityCreate(BaseModel):
    community_id: UUID4
    name: str
    description: str
    owner_id: str
    members: List[str]
    keywords: List[str]

class CommunityUpdate(BaseModel):
    name: str
    description: str
    members: List[str]
    keywords: List[str]
