import json
from typing import Any, Dict, List
from app.services.content_processor_service import ContentProcessorService
from app.services.webscraper_service import WebScraperService
from app.services.knowledge_source_service import KnowledgeSourceService, KnowledgeSourceUpdate
from app.lib.dynamodb_controller import DynamoDBController
from app.lib.sqs_controller import SQSController
import logging
import os

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    # Initialize your custom logger
    logger = logging.getLogger()

    logger.info("Lambda handler started with event: %s", json.dumps(event))
    
    # Extract necessary information from the event
    community_id = event.get('community_id')
    source_id = event.get('source_id')
    url = event.get('url')
    
    if not community_id or not source_id or not url:
        logger.error("Missing required parameters: community_id, source_id, or url")
        return {
            'statusCode': 400,
            'body': json.dumps('Community ID, Source ID, and URL are required')
        }

    # Initialize services
    scraper_service = WebScraperService(logger=logger)
    content_processor_service = ContentProcessorService(logger=logger)
    dynamodb_controller = DynamoDBController('sharp_app_data', logger=logger)
    knowledge_source_service = KnowledgeSourceService(dynamodb_controller, logger=logger)

    # Initialize SQS controller
    sqs_queue_url = os.getenv('KNOWLEDGE_SOURCE_CHUNK_PROCESSING_QUEUE')
    sqs_controller = SQSController(queue_url=sqs_queue_url, logger=logger)

    # Update knowledge source status to "Processing"
    update_data = KnowledgeSourceUpdate(source_status="Processing")
    knowledge_source_service.update_knowledge_source(community_id, source_id, update_data)
    logger.info("Knowledge source status updated to 'Processing' for community_id: %s, source_id: %s", community_id, source_id)
    
    # Scrape the content
    content = scraper_service.scrape_content(url)
    
    if content is None:
        # Update knowledge source status to "Failed"
        update_data = KnowledgeSourceUpdate(source_status="Failed")
        knowledge_source_service.update_knowledge_source(community_id, source_id, update_data)
        logger.error("Failed to scrape content from the URL: %s", url)
        return {
            'statusCode': 500,
            'body': json.dumps('Failed to scrape content from the provided URL')
        }
    
    # Chunk the content
    chunks = content_processor_service.split_content(content, 4000)
    logger.info("Content chunked into %d parts", len(chunks))
    
    # Send each chunk as an SQS message
    send_chunk_messages(sqs_controller, community_id, source_id, chunks)
    
    # Store the chunks in DynamoDB (optional, depending on your workflow)
    knowledge_source_service.store_chunks(community_id, source_id, chunks)
    logger.info("Chunks stored in DynamoDB for community_id: %s, source_id: %s", community_id, source_id)

    # Update knowledge source status to "Completed"
    update_data = KnowledgeSourceUpdate(source_status="Completed")
    knowledge_source_service.update_knowledge_source(community_id, source_id, update_data)
    logger.info("Knowledge source status updated to 'Completed' for community_id: %s, source_id: %s", community_id, source_id)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Content scraped, chunked, and stored successfully',
            'chunks': chunks
        })
    }

def send_chunk_messages(sqs_controller: SQSController, community_id: str, source_id: str, chunks: List[str]) -> None:
    for idx, chunk in enumerate(chunks):
        message = {
            'community_id': community_id,
            'source_id': source_id,
            'chunk_id': idx,  # Adding an index to identify the chunk
            'chunk_content': chunk,
            'message_type': 'chunk'  # Include metadata to identify the message type
        }
        sqs_controller.send_message(
            message_body=json.dumps(message)
        )
