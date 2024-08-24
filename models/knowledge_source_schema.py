from pydantic import BaseModel, HttpUrl, UUID4
from typing import Optional

class KnowledgeSourceCreate(BaseModel):
    source_id: UUID4
    community_id: UUID4
    url: HttpUrl
    processing_status: str = "Pending"  # Default status is pending

class KnowledgeSourceUpdate(BaseModel):
    processing_status: Optional[str] = None
    ingestion_timestamp: Optional[int] = None
