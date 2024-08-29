import json
from typing import Any, Dict, List
from app.services.content_processor_service import ContentProcessorService
from app.services.webscraper_service import WebScraperService
from app.services.knowledge_source_service import KnowledgeSourceService, KnowledgeSourceUpdate
from app.lib.dynamodb_controller import DynamoDBController

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    # Extract necessary information from the event
    community_id = event.get('community_id')
    source_id = event.get('source_id')
    url = event.get('url')
    
    if not community_id or not source_id or not url:
        return {
            'statusCode': 400,
            'body': json.dumps('Community ID, Source ID, and URL are required')
        }

    # Initialize services
    scraper_service = WebScraperService()
    content_processor_service = ContentProcessorService()
    dynamodb_controller = DynamoDBController('sharp_app_data')
    knowledge_source_service = KnowledgeSourceService(dynamodb_controller)

    # Update knowledge source status to "Processing"
    update_data = KnowledgeSourceUpdate(source_status="Processing")
    knowledge_source_service.update_knowledge_source(community_id, source_id, update_data)
    
    # Scrape the content
    content = scraper_service.scrape_content(url)
    
    if content is None:
        # Update knowledge source status to "Failed"
        update_data = KnowledgeSourceUpdate(source_status="Failed")
        knowledge_source_service.update_knowledge_source(community_id, source_id, update_data)
        return {
            'statusCode': 500,
            'body': json.dumps('Failed to scrape content from the provided URL')
        }
    
    # Chunk the content
    chunks = content_processor_service.split_content(content)
    
    # Store the chunks in DynamoDB
    knowledge_source_service.store_chunks(community_id, source_id, chunks)

    # Update knowledge source status to "Completed"
    update_data = KnowledgeSourceUpdate(source_status="Completed")
    knowledge_source_service.update_knowledge_source(community_id, source_id, update_data)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Content scraped, chunked, and stored successfully',
            'chunks': chunks
        })
    }
