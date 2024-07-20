from pydantic import BaseModel, UUID4
from typing import List, Optional

class CommunityCreate(BaseModel):
    community_id: UUID4
    name: str
    description: str
    owner_ids: Optional[List[str]] = None
    members: List[str]
    keywords: List[str]
    updated_at: Optional[str] = None

class CommunityUpdate(BaseModel):
    name: str
    description: str
    members: List[str]
    keywords: List[str]

class OwnerAdd(BaseModel):
    user_id: str
    role: str

class MemberAdd(BaseModel):
    user_id: str
    role: str
