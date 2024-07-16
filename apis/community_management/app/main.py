from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from mangum import Mangum
from app.services.cognito_service import get_current_user
from app.services.community_service import CommunityService
from app.lib.dynamodb_controller import DynamoDBController
from app.models.community import CommunityCreate, CommunityUpdate
from pydantic import UUID4
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
        logger.info("Received request to list communities")
        communities = community_service.list_communities()
        logger.info("Communities listed successfully")
        return {"communities": communities}
    except ClientError as e:
        logger.error(f"Error listing communities: {e}")
        raise HTTPException(status_code=500, detail="Error listing communities")
    except Exception as e:
        logger.error(f"Unexpected error listing communities: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/communities/{community_id}")
def read_community(community_id: UUID4, current_user: dict = Depends(get_current_user)):
    try:
        logger.info(f"Received request to read community with ID: {community_id}")
        community = community_service.get_community(str(community_id))
        if community:
            logger.info(f"Community {community_id} retrieved successfully")
            return community
        logger.error(f"Community {community_id} not found")
        raise HTTPException(status_code=404, detail="Community not found")
    except ClientError as e:
        logger.error(f"Error getting community: {e}")
        raise HTTPException(status_code=500, detail="Error getting community")
    except Exception as e:
        logger.error(f"Unexpected error getting community: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/communities/")
def create_community(community: CommunityCreate, current_user: dict = Depends(get_current_user)):
    try:
        logger.info(f"Received request to create community with ID: {community.community_id}")
        logger.debug(f"Community data: {community}")

        existing_community = community_service.get_community(str(community.community_id))
        if existing_community:
            logger.error(f"Community ID {community.community_id} already exists")
            raise HTTPException(status_code=400, detail="Community ID already exists")

        new_community = {
            "community_id": str(community.community_id),
            "name": community.name,
            "description": community.description,
            "owner_id": community.owner_id,
            "members": community.members,
            "keywords": community.keywords
        }
        community_service.create_community(new_community)
        logger.info(f"Community {community.community_id} created successfully")
        return {"message": "Community created successfully"}
    except ClientError as e:
        logger.error(f"Error creating community: {e}")
        raise HTTPException(status_code=500, detail="Error creating community")
    except Exception as e:
        logger.error(f"Unexpected error creating community: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/communities/{community_id}")
def update_community(community_id: UUID4, community: CommunityUpdate, current_user: dict = Depends(get_current_user)):
    try:
        logger.info(f"Received request to update community with ID: {community_id}")
        logger.debug(f"Update data: {community}")

        existing_community = community_service.get_community(str(community_id))
        if not existing_community:
            logger.error(f"Community {community_id} not found")
            raise HTTPException(status_code=404, detail="Community not found")

        updated_community = {
            "name": community.name,
            "description": community.description,
            "members": community.members,
            "keywords": community.keywords
        }
        community_service.update_community(str(community_id), updated_community)
        logger.info(f"Community {community_id} updated successfully")
        return {"message": "Community updated successfully"}
    except ClientError as e:
        logger.error(f"Error updating community: {e}")
        raise HTTPException(status_code=500, detail="Error updating community")
    except Exception as e:
        logger.error(f"Unexpected error updating community: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/communities/{community_id}")
def delete_community(community_id: UUID4, current_user: dict = Depends(get_current_user)):
    try:
        logger.info(f"Received request to delete community with ID: {community_id}")
        community = community_service.get_community(str(community_id))
        if not community:
            logger.error(f"Community {community_id} not found")
            raise HTTPException(status_code=404, detail="Community not found")
        community_service.delete_community(str(community_id))
        logger.info(f"Community {community_id} deleted successfully")
        return {"message": "Community deleted successfully"}
    except ClientError as e:
        logger.error(f"Error deleting community: {e}")
        raise HTTPException(status_code=500, detail="Error deleting community")
    except Exception as e:
        logger.error(f"Unexpected error deleting community: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

handler = Mangum(app)
