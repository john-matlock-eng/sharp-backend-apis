from pydantic import BaseModel, Field
from datetime import datetime

class UserModel(BaseModel):
    user_id: str = Field(..., alias='PK')
    profile: str = Field('PROFILE', alias='SK')
    entity_type: str = Field('User', alias='EntityType')
    name: str = Field(..., alias='Name')
    joined_at: datetime = Field(..., alias='JoinedAt')
