from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID

class CommunityCreate(BaseModel):
    community_id: UUID
    community_name: str
    description: str
    members: List[UUID]
    keywords: List[str]
    created_at: int = Field(default_factory=lambda: int(datetime.now(timezone.utc).timestamp()))
    owner_ids: Optional[List[UUID]] = []

class CommunityUpdate(BaseModel):
    community_name: Optional[str]
    owner_ids: Optional[List[str]]

class OwnerAdd(BaseModel):
    user_id: UUID

class MemberAdd(BaseModel):
    user_id: UUID
    joined_at: int = Field(default_factory=lambda: int(datetime.now(timezone.utc).timestamp()))
