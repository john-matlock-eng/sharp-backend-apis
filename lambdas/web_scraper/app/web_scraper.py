import json
from typing import Any, Dict
from app.services.webscraper_service import WebScraperService

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    url = event.get('url')
    
    if not url:
        return {
            'statusCode': 400,
            'body': json.dumps('URL is required')
        }

    scraper_service = WebScraperService()
    content = scraper_service.scrape_content(url)
    
    if content is None:
        return {
            'statusCode': 500,
            'body': json.dumps('Failed to scrape content from the provided URL')
        }

    return {
        'statusCode': 200,
        'body': json.dumps({'content': content})
    }
