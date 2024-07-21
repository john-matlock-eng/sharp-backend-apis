from pydantic import BaseModel, Field
from datetime import datetime

class CommunityMemberModel(BaseModel):
    community_id: str = Field(..., alias='PK')
    member_id: str = Field(..., alias='SK')
    entity_type: str = Field('CommunityMember', alias='EntityType')
    joined_at: datetime = Field(..., alias='JoinedAt')
