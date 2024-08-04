from pydantic import BaseModel, UUID4, Field
from datetime import datetime

class CommunityMemberModel(BaseModel):
    community_id: UUID4
    member_id: UUID4
    joined_at: datetime

    class Config:
        orm_mode = True
