from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import UUID4
import os
import logging
from botocore.exceptions import ClientError
from app.services.community_service import CommunityService
from app.services.cognito_service import get_current_user
from app.lib.dynamodb_controller import DynamoDBController
from app.models.community_schema import CommunityCreate, CommunityUpdate, OwnerAdd, MemberAdd

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
    """Root endpoint to check API status.

    Returns:
        dict: Welcome message.
    """
    logger.info("Root endpoint called")
    return {"message": "Welcome to the Community Management API"}

@app.get("/communities/")
def list_communities(current_user: dict = Depends(get_current_user)):
    """List all communities.

    Args:
        current_user (dict): Current authenticated user.

    Returns:
        dict: A dictionary containing a list of communities.

    Raises:
        HTTPException: If there is an error listing communities.
    """
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
    """Read a community by its ID.

    Args:
        community_id (UUID4): ID of the community to read.
        current_user (dict): Current authenticated user.

    Returns:
        dict: The community model.

    Raises:
        HTTPException: If the community is not found or if there is an error.
    """
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
    """Create a new community.

    Args:
        community (CommunityCreate): Community creation data.
        current_user (dict): Current authenticated user.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If there is an error creating the community.
    """
    try:
        logger.info(f"Received request to create community with ID: {community.community_id}")
        logger.debug(f"Community data: {community}")

        existing_community = community_service.get_community(str(community.community_id))
        if existing_community:
            logger.error(f"Community ID {community.community_id} already exists")
            raise HTTPException(status_code=400, detail="Community ID already exists")

        community_service.create_community(community)
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
    """Update a community by its ID.

    Args:
        community_id (UUID4): ID of the community to update.
        community (CommunityUpdate): Community update data.
        current_user (dict): Current authenticated user.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If the community is not found or if there is an error updating the community.
    """
    try:
        logger.info(f"Received request to update community with ID: {community_id}")
        logger.debug(f"Update data: {community}")

        existing_community = community_service.get_community(str(community_id))
        if not existing_community:
            logger.error(f"Community {community_id} not found")
            raise HTTPException(status_code=404, detail="Community not found")

        community_service.update_community(str(community_id), community)
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
    """Delete a community by its ID.

    Args:
        community_id (UUID4): ID of the community to delete.
        current_user (dict): Current authenticated user.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If the community is not found or if there is an error deleting the community.
    """
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

@app.post("/communities/{community_id}/owners/")
def add_owners(community_id: UUID4, owner: OwnerAdd, current_user: dict = Depends(get_current_user)):
    """Add an owner to a community.

    Args:
        community_id (UUID4): ID of the community.
        owner (OwnerAdd): Owner addition data.
        current_user (dict): Current authenticated user.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If there is an error adding the owner.
    """
    try:
        logger.info(f"Received request to add owner to community with ID: {community_id}")
        community_service.add_owner(str(community_id), owner)
        logger.info(f"Owner {owner.user_id} added to community {community_id} successfully")
        return {"message": "Owner added successfully"}
    except ClientError as e:
        logger.error(f"Error adding owner: {e}")
        raise HTTPException(status_code=500, detail="Error adding owner")
    except Exception as e:
        logger.error(f"Unexpected error adding owner: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/communities/{community_id}/owners/{user_id}")
def remove_owners(community_id: UUID4, user_id: UUID4, current_user: dict = Depends(get_current_user)):
    """Remove an owner from a community.

    Args:
        community_id (UUID4): ID of the community.
        user_id (UUID4): ID of the user to remove as owner.
        current_user (dict): Current authenticated user.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If there is an error removing the owner.
    """
    try:
        logger.info(f"Received request to remove owner {user_id} from community {community_id}")
        community_service.remove_owner(str(community_id), str(user_id))
        logger.info(f"Owner {user_id} removed from community {community_id} successfully")
        return {"message": "Owner removed successfully"}
    except ClientError as e:
        logger.error(f"Error removing owner: {e}")
        raise HTTPException(status_code=500, detail="Error removing owner")
    except Exception as e:
        logger.error(f"Unexpected error removing owner: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/communities/{community_id}/members/")
def add_members(community_id: UUID4, member: MemberAdd, current_user: dict = Depends(get_current_user)):
    """Add a member to a community.

    Args:
        community_id (UUID4): ID of the community.
        member (MemberAdd): Member addition data.
        current_user (dict): Current authenticated user.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If there is an error adding the member.
    """
    try:
        logger.info(f"Received request to add member to community with ID: {community_id}")
        community_service.add_member(str(community_id), member)
        logger.info(f"Member {member.user_id} added to community {community_id} successfully")
        return {"message": "Member added successfully"}
    except ClientError as e:
        logger.error(f"Error adding member: {e}")
        raise HTTPException(status_code=500, detail="Error adding member")
    except Exception as e:
        logger.error(f"Unexpected error adding member: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/communities/{community_id}/members/{user_id}")
def remove_members(community_id: UUID4, user_id: UUID4, current_user: dict = Depends(get_current_user)):
    """Remove a member from a community.

    Args:
        community_id (UUID4): ID of the community.
        user_id (UUID4): ID of the user to remove as member.
        current_user (dict): Current authenticated user.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If there is an error removing the member.
    """
    try:
        logger.info(f"Received request to remove member {user_id} from community {community_id}")
        community_service.remove_member(str(community_id), str(user_id))
        logger.info(f"Member {user_id} removed from community {community_id} successfully")
        return {"message": "Member removed successfully"}
    except ClientError as e:
        logger.error(f"Error removing member: {e}")
        raise HTTPException(status_code=500, detail="Error removing member")
    except Exception as e:
        logger.error(f"Unexpected error removing member: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
