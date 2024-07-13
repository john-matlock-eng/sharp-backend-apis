from fastapi import FastAPI, HTTPException, Depends
from mangum import Mangum
from app.services.community_service import CommunityService
from app.lib.dynamodb_controller import DynamoDBController
from app.models.community import CommunityCreate, CommunityUpdate
import os
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize DynamoDB controller and community service
table_name = os.getenv('TABLE_NAME', 'sharp_app_data')
dynamodb_controller = DynamoDBController(table_name)
community_service = CommunityService(dynamodb_controller)

@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"message": "Welcome to the Community Management API"}

@app.get("/communities/{community_id}")
def read_community(community_id: int):
    community = community_service.get_community(community_id)
    if community:
        logger.info(f"Community {community_id} retrieved successfully")
        return community
    logger.error(f"Community {community_id} not found")
    raise HTTPException(status_code=404, detail="Community not found")

@app.post("/communities/")
def create_community(community: CommunityCreate):
    existing_community = community_service.get_community(community.community_id)
    if existing_community:
        logger.error(f"Community ID {community.community_id} already exists")
        raise HTTPException(status_code=400, detail="Community ID already exists")
    community_service.create_community(community.community_id, community.name)
    logger.info(f"Community {community.community_id} created successfully")
    return {"message": "Community created successfully"}

@app.put("/communities/{community_id}")
def update_community(community_id: int, community: CommunityUpdate):
    existing_community = community_service.get_community(community_id)
    if not existing_community:
        logger.error(f"Community {community_id} not found")
        raise HTTPException(status_code=404, detail="Community not found")
    community_service.update_community(community_id, community.name)
    logger.info(f"Community {community_id} updated successfully")
    return {"message": "Community updated successfully"}

@app.delete("/communities/{community_id}")
def delete_community(community_id: int):
    community = community_service.get_community(community_id)
    if not community:
        logger.error(f"Community {community_id} not found")
        raise HTTPException(status_code=404, detail="Community not found")
    community_service.delete_community(community_id)
    logger.info(f"Community {community_id} deleted successfully")
    return {"message": "Community deleted successfully"}

# Create a handler for AWS Lambda
handler = Mangum(app)
