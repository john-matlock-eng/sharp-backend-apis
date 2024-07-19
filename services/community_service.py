import logging
from functools import wraps
from typing import Dict, Any, List, Optional
from boto3.dynamodb.conditions import Key
from app.lib.dynamodb_controller import DynamoDBController
from app.models.community_schema import CommunityCreate, CommunityUpdate, OwnerAdd, MemberAdd

class CommunityService:
    """Service class for managing community operations."""

    def __init__(self, dynamodb_controller: DynamoDBController):
        """Initializes the CommunityService with a DynamoDBController.

        Args:
            dynamodb_controller (DynamoDBController): The DynamoDB controller instance.
        """
        self.dynamodb_controller = dynamodb_controller
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def log_and_handle_exceptions(method):
        """Decorator for logging method calls and handling exceptions."""
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            try:
                self.logger.info(f"Calling {method.__name__} with args: {args}, kwargs: {kwargs}")
                result = method(self, *args, **kwargs)
                self.logger.info(f"{method.__name__} completed successfully")
                return result
            except Exception as e:
                self.logger.error(f"Unexpected error in {method.__name__}: {e}")
                raise
        return wrapper

    @log_and_handle_exceptions
    def create_community(self, community: CommunityCreate) -> None:
        """Creates a new community.

        Args:
            community (CommunityCreate): The community data to create.
        """
        new_community = {
            "PK": f"COMMUNITY#{community.community_id}",
            "SK": f"METADATA#{community.community_id}",
            "community_id": str(community.community_id),
            "name": community.name,
            "description": community.description,
            "owner_ids": community.owner_ids,
            "members": community.members,
            "keywords": community.keywords,
            "EntityType": "community",
            "CreatedAt": community.created_at
        }
        self.dynamodb_controller.put_item(new_community)

    @log_and_handle_exceptions
    def get_community(self, community_id: str) -> Optional[Dict[str, Any]]:
        """Fetches a community by its ID.

        Args:
            community_id (str): The ID of the community to fetch.

        Returns:
            Optional[Dict[str, Any]]: The fetched community item.
        """
        pk = f"COMMUNITY#{community_id}"
        sk = f"METADATA#{community_id}"
        return self.dynamodb_controller.get_item(pk, sk)

    @log_and_handle_exceptions
    def update_community(self, community_id: str, update_data: CommunityUpdate) -> None:
        """Updates a community by its ID.

        Args:
            community_id (str): The ID of the community to update.
            update_data (CommunityUpdate): The data to update in the community.
        """
        pk = f"COMMUNITY#{community_id}"
        sk = f"METADATA#{community_id}"
        self.dynamodb_controller.update_item(pk, sk, update_data.dict())

    @log_and_handle_exceptions
    def delete_community(self, community_id: str) -> None:
        """Deletes a community by its ID.

        Args:
            community_id (str): The ID of the community to delete.
        """
        pk = f"COMMUNITY#{community_id}"
        sk = f"METADATA#{community_id}"
        self.dynamodb_controller.delete_item(pk, sk)

    @log_and_handle_exceptions
    def list_communities(self) -> List[Dict[str, Any]]:
        """Lists all communities.

        Returns:
            List[Dict[str, Any]]: A list of community items.
        """
        key_condition_expression = Key('SK').eq("METADATA")
        items, _ = self.dynamodb_controller.query_with_pagination(
            key_condition=key_condition_expression,
            index_name="GSI1"
        )
        return items

    @log_and_handle_exceptions
    def add_owner(self, community_id: str, owner: OwnerAdd) -> None:
        """Adds an owner to a community.

        Args:
            community_id (str): The ID of the community.
            owner (OwnerAdd): The owner data to add.
        """
        owner_item = {
            "PK": f"COMMUNITY#{community_id}",
            "SK": f"OWNER#{owner.user_id}",
            "user_id": owner.user_id,
            "role": owner.role
        }
        self.dynamodb_controller.put_item(owner_item)

    @log_and_handle_exceptions
    def remove_owner(self, community_id: str, user_id: str) -> None:
        """Removes an owner from a community.

        Args:
            community_id (str): The ID of the community.
            user_id (str): The ID of the user to remove as owner.
        """
        pk = f"COMMUNITY#{community_id}"
        sk = f"OWNER#{user_id}"
        self.dynamodb_controller.delete_item(pk, sk)

    @log_and_handle_exceptions
    def add_member(self, community_id: str, member: MemberAdd) -> None:
        """Adds a member to a community.

        Args:
            community_id (str): The ID of the community.
            member (MemberAdd): The member data to add.
        """
        member_item = {
            "PK": f"COMMUNITY#{community_id}",
            "SK": f"MEMBER#{member.user_id}",
            "user_id": member.user_id,
            "role": member.role
        }
        self.dynamodb_controller.put_item(member_item)

    @log_and_handle_exceptions
    def remove_member(self, community_id: str, user_id: str) -> None:
        """Removes a member from a community.

        Args:
            community_id (str): The ID of the community.
            user_id (str): The ID of the user to remove as member.
        """
        pk = f"COMMUNITY#{community_id}"
        sk = f"MEMBER#{user_id}"
        self.dynamodb_controller.delete_item(pk, sk)
