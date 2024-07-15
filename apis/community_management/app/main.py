from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from mangum import Mangum
from app.services.cognito_service import get_current_user
from app.services.community_service import CommunityService
from app.lib.dynamodb_controller import DynamoDBController
from app.models.community import CommunityCreate, CommunityUpdate
import os
import logging
from botocore.exceptions import ClientError

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="https://your_cognito_domain/oauth2/token")

app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DynamoDB controller and community service
table_name = os.getenv('TABLE_NAME', 'sharp_app_data')
dynamodb_controller = DynamoDBController(table_name)
community_service = CommunityService(dynamodb_controller)

@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"message": "Welcome to the Community Management API"}

@app.get("/communities/")
def list_communities(current_user: dict = Depends(get_current_user)):
    try:
        communities = community_service.list_communities()
        return {"communities": communities}
    except ClientError as e:
        logger.error(f"Error listing communities: {e}")
        raise HTTPException(status_code=500, detail="Error listing communities")

@app.get("/communities/{community_id}")
def read_community(community_id: int, current_user: dict = Depends(get_current_user)):
    try:
        community = community_service.get_community(community_id)
        if community:
            logger.info(f"Community {community_id} retrieved successfully")
            return community
        logger.error(f"Community {community_id} not found")
        raise HTTPException(status_code=404, detail="Community not found")
    except ClientError as e:
        logger.error(f"Error getting community: {e}")
        raise HTTPException(status_code=500, detail="Error getting community")

@app.post("/communities/")
def create_community(community: CommunityCreate, current_user: dict = Depends(get_current_user)):
    try:
        existing_community = community_service.get_community(community.community_id)
        if existing_community:
            logger.error(f"Community ID {community.community_id} already exists")
            raise HTTPException(status_code=400, detail="Community ID already exists")
        community_service.create_community(community.community_id, community.name)
        logger.info(f"Community {community.community_id} created successfully")
        return {"message": "Community created successfully"}
    except ClientError as e:
        logger.error(f"Error creating community: {e}")
        raise HTTPException(status_code=500, detail="Error creating community")

@app.put("/communities/{community_id}")
def update_community(community_id: int, community: CommunityUpdate, current_user: dict = Depends(get_current_user)):
    try:
        existing_community = community_service.get_community(community_id)
        if not existing_community:
            logger.error(f"Community {community_id} not found")
            raise HTTPException(status_code=404, detail="Community not found")
        community_service.update_community(community_id, community.name)
        logger.info(f"Community {community_id} updated successfully")
        return {"message": "Community updated successfully"}
    except ClientError as e:
        logger.error(f"Error updating community: {e}")
        raise HTTPException(status_code=500, detail="Error updating community")

@app.delete("/communities/{community_id}")
def delete_community(community_id: int, current_user: dict = Depends(get_current_user)):
    try:
        community = community_service.get_community(community_id)
        if not community:
            logger.error(f"Community {community_id} not found")
            raise HTTPException(status_code=404, detail="Community not found")
        community_service.delete_community(community_id)
        logger.info(f"Community {community_id} deleted successfully")
        return {"message": "Community deleted successfully"}
    except ClientError as e:
        logger.error(f"Error deleting community: {e}")
        raise HTTPException(status_code=500, detail="Error deleting community")

# Create a handler for AWS Lambda
handler = Mangum(app)
