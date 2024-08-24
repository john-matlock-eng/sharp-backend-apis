import logging
from pydantic import BaseModel, HttpUrl, UUID4
from typing import Optional, Dict, Any, List, Tuple
from boto3.dynamodb.conditions import Key
from app.lib.dynamodb_controller import DynamoDBController
from app.lib.logging import log_and_handle_exceptions
from datetime import datetime, timezone
import uuid
import os

# Define the Pydantic models for knowledge source creation and updates
class KnowledgeSourceCreate(BaseModel):
    source_id: UUID4
    community_id: UUID4
    url: HttpUrl
    source_status: str = "Pending"  # Default status is pending

class KnowledgeSourceUpdate(BaseModel):
    source_status: Optional[str] = None
    ingestion_timestamp: Optional[int] = None

# Define the KnowledgeSourceService class
class KnowledgeSourceService:
    def __init__(self, dynamodb_controller: DynamoDBController):
        self.dynamodb_controller = dynamodb_controller
        self.logger = logging.getLogger(__name__)

    @log_and_handle_exceptions
    def create_knowledge_source(self, knowledge_source: KnowledgeSourceCreate) -> None:
        item = {
            'PK': 'KNOWLEDGE_SOURCE',
            'SK': f'COMMUNITY#{knowledge_source.community_id}#KNOWLEDGE_SOURCE#{knowledge_source.source_id}',
            'EntityType': 'KnowledgeSource',
            'CreatedAt': int(datetime.now(timezone.utc).timestamp()),
            'source_id': str(knowledge_source.source_id),
            'community_id': str(knowledge_source.community_id),
            'url': str(knowledge_source.url),
            'source_status': knowledge_source.source_status,
        }
        self.dynamodb_controller.put_item(item)

    @log_and_handle_exceptions
    def update_knowledge_source(self, community_id: str, source_id: str, update_data: KnowledgeSourceUpdate) -> None:
        sk = f'COMMUNITY#{community_id}#KNOWLEDGE_SOURCE#{source_id}'
        update_data_dict = update_data.dict(exclude_unset=True)
        
        if not update_data_dict:
            self.logger.warning("No update data provided; skipping update.")
            return  # Skip the update if there's no data to update
        
        if 'ingestion_timestamp' in update_data_dict:
            update_data_dict['ingestion_timestamp'] = int(datetime.now(timezone.utc).timestamp())
        
        self.dynamodb_controller.update_item('KNOWLEDGE_SOURCE', sk, update_data_dict)

    @log_and_handle_exceptions
    def store_chunks(self, community_id: str, source_id: str, chunks: List[Dict[str, Any]]) -> None:
        for chunk in chunks:
            chunk_id = str(uuid.uuid4())  # Generate a unique ID for each chunk
            item = {
                'PK': 'KNOWLEDGE_SOURCE_CHUNK',
                'SK': f'COMMUNITY#{community_id}#KNOWLEDGE_SOURCE#{source_id}#CHUNK#{chunk_id}',
                'EntityType': 'KnowledgeSourceChunk',
                'source_id': source_id,
                'community_id': community_id,
                'chunk_id': chunk_id,
                'data': chunk,
                'CreatedAt': int(datetime.now(timezone.utc).timestamp()),
            }
            self.dynamodb_controller.put_item(item)

    @log_and_handle_exceptions
    def store_combined_output(self, community_id: str, source_id: str, combined_output: Dict[str, Any]) -> None:
        item = {
            'PK': 'KNOWLEDGE_SOURCE_UNCHUNK',
            'SK': f'COMMUNITY#{community_id}#KNOWLEDGE_SOURCE#{source_id}',
            'EntityType': 'KnowledgeSourceUnchunk',
            'source_id': source_id,
            'community_id': community_id,
            'data': combined_output,
            'CreatedAt': int(datetime.now(timezone.utc).timestamp()),
        }
        self.dynamodb_controller.put_item(item)

    @log_and_handle_exceptions
    def get_knowledge_source(self, community_id: str, source_id: str) -> Optional[Dict[str, Any]]:
        sk = f'COMMUNITY#{community_id}#KNOWLEDGE_SOURCE#{source_id}'
        return self.dynamodb_controller.get_item('KNOWLEDGE_SOURCE', sk)
    
    @log_and_handle_exceptions
    def list_knowledge_sources(self, community_id: str, limit: int = 20, last_evaluated_key: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        partition_key = Key('PK').eq('KNOWLEDGE_SOURCE')
        sort_key_condition = Key('SK').begins_with(f'COMMUNITY#{community_id}#KNOWLEDGE_SOURCE#')
        items, last_key = self.dynamodb_controller.query_with_pagination(
            partition_key, sort_key_condition, limit=limit, last_evaluated_key=last_evaluated_key
        )
        return items, last_key

    @log_and_handle_exceptions
    def delete_knowledge_source(self, community_id: str, source_id: str) -> None:
        sk = f'COMMUNITY#{community_id}#KNOWLEDGE_SOURCE#{source_id}'
        self.dynamodb_controller.delete_item('KNOWLEDGE_SOURCE', sk)

        # Delete all related chunks
        chunk_key_condition = Key('SK').begins_with(f'COMMUNITY#{community_id}#KNOWLEDGE_SOURCE#{source_id}#CHUNK#')
        chunks, _ = self.dynamodb_controller.query_with_pagination(
            Key('PK').eq('KNOWLEDGE_SOURCE_CHUNK'), chunk_key_condition
        )
        for chunk in chunks:
            self.dynamodb_controller.delete_item('KNOWLEDGE_SOURCE_CHUNK', chunk['SK'])

        # Delete the unchunked data
        unchunk_sk = f'COMMUNITY#{community_id}#KNOWLEDGE_SOURCE#{source_id}'
        self.dynamodb_controller.delete_item('KNOWLEDGE_SOURCE_UNCHUNK', unchunk_sk)

# Define a factory function to create an instance of KnowledgeSourceService
def get_knowledge_source_service() -> KnowledgeSourceService:
    table_name = os.getenv('TABLE_NAME', 'sharp_app_data')
    dynamodb_controller = DynamoDBController(table_name)
    return KnowledgeSourceService(dynamodb_controller)
