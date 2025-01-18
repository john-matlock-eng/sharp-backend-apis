import json
from typing import Any, Dict, List
from app.services.content_processor_service import ContentProcessorService
from app.services.knowledge_source_service import KnowledgeSourceService, KnowledgeSourceUpdate
from app.lib.dynamodb_controller import DynamoDBController
import logging

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    # Initialize logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Initialize services
    dynamodb_controller = DynamoDBController('sharp_app_data')
    knowledge_source_service = KnowledgeSourceService(dynamodb_controller)
    content_processor_service = ContentProcessorService()

    # Loop through SQS messages
    for record in event['Records']:
        try:
            # Extract message body
            message_body = json.loads(record['body'])
            logger.info(f"Processing message: {message_body}")

            community_id = message_body['community_id']
            source_id = message_body['source_id']
            chunk_content = message_body['chunk_content']

            # Process content chunk using the OpenAI controller
            processed_content = content_processor_service.process_content(chunk_content)

            # Store the processed chunk (this might involve updating the database or performing other tasks)
            knowledge_source_service.store_chunk(community_id, source_id, processed_content)

            # Optionally update status or handle post-processing steps
            update_data = KnowledgeSourceUpdate(source_status="Processed")
            knowledge_source_service.update_knowledge_source(community_id, source_id, update_data)
            logger.info(f"Successfully processed and stored chunk for community_id: {community_id}, source_id: {source_id}")

        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            # Handle error and decide whether to requeue, send to DLQ, etc.

    return {
        'statusCode': 200,
        'body': json.dumps('Processed all chunks successfully')
    }
