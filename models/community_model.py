from pydantic import BaseModel, Field
from datetime import datetime

class CommunityModel(BaseModel):
    community_id: str = Field(..., alias='PK')
    details: str = Field('DETAILS', alias='SK')
    entity_type: str = Field('Community', alias='EntityType')
    community_name: str = Field(..., alias='CommunityName')
    owner_id: str = Field(..., alias='OwnerID')
    created_at: datetime = Field(..., alias='CreatedAt')