import logging
from functools import wraps
from typing import Type, Dict, Any, List
from botocore.exceptions import ClientError
from pynamodb.models import Model
from pynamodb.exceptions import PynamoDBException
from app.lib.dynamodb_controller import DynamoDBController
from app.models.community_schema import CommunityCreate, CommunityUpdate

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
            except PynamoDBException as e:
                self.logger.error(f"DynamoDB error in {method.__name__}: {e}")
                raise
            except ClientError as e:
                self.logger.error(f"Client error in {method.__name__}: {e}")
                raise
            except ValueError as e:
                self.logger.error(f"Validation error in {method.__name__}: {e}")
                raise
            except Exception as e:
                self.logger.error(f"Unexpected error in {method.__name__}: {e}")
                raise
        return wrapper

    def _validate_model_class(self, model_class: Type[Model]) -> None:
        """Validates the model class.

        Args:
            model_class (Type[Model]): The model class to validate.

        Raises:
            ValueError: If the model class is not a subclass of pynamodb.models.Model.
        """
        if not issubclass(model_class, Model):
            raise ValueError(f"{model_class} is not a subclass of pynamodb.models.Model")

    def _validate_key(self, key: str, key_name: str) -> None:
        """Validates the key.

        Args:
            key (str): The key to validate.
            key_name (str): The name of the key being validated.

        Raises:
            ValueError: If the key is not a non-empty string.
        """
        if not isinstance(key, str) or not key:
            raise ValueError(f"{key_name} must be a non-empty string")

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
            "keywords": community.keywords
        }
        self.dynamodb_controller.put_item(new_community)

    @log_and_handle_exceptions
    def get_community(self, model_class: Type[Model], community_id: str) -> Model:
        """Fetches a community by its ID.

        Args:
            model_class (Type[Model]): The model class of the community.
            community_id (str): The ID of the community to fetch.

        Returns:
            Model: The fetched community item.

        Raises:
            ValueError: If the community_id is invalid.
        """
        self._validate_model_class(model_class)
        self._validate_key(community_id, "Community ID")
        pk = f"COMMUNITY#{community_id}"
        sk = f"METADATA#{community_id}"
        return self.dynamodb_controller.get_item(model_class, pk, sk)

    @log_and_handle_exceptions
    def update_community(self, model_class: Type[Model], community_id: str, update_data: CommunityUpdate) -> None:
        """Updates a community by its ID.

        Args:
            model_class (Type[Model]): The model class of the community.
            community_id (str): The ID of the community to update.
            update_data (CommunityUpdate): The data to update in the community.

        Raises:
            ValueError: If the community_id or update_data is invalid.
        """
        self._validate_model_class(model_class)
        self._validate_key(community_id, "Community ID")
        pk = f"COMMUNITY#{community_id}"
        sk = f"METADATA#{community_id}"
        update_dict = update_data.dict()
        self.dynamodb_controller.update_item(model_class, pk, sk, update_dict)

    @log_and_handle_exceptions
    def delete_community(self, model_class: Type[Model], community_id: str) -> None:
        """Deletes a community by its ID.

        Args:
            model_class (Type[Model]): The model class of the community.
            community_id (str): The ID of the community to delete.

        Raises:
            ValueError: If the community_id is invalid.
        """
        self._validate_model_class(model_class)
        self._validate_key(community_id, "Community ID")
        pk = f"COMMUNITY#{community_id}"
        sk = f"METADATA#{community_id}"
        self.dynamodb_controller.delete_item(model_class, pk, sk)

    @log_and_handle_exceptions
    def list_communities(self, model_class: Type[Model]) -> List[Model]:
        """Lists all communities.

        Args:
            model_class (Type[Model]): The model class of the communities.

        Returns:
            List[Model]: A list of community items.
        """
        self._validate_model_class(model_class)
        key_condition_expression = model_class.PK.startswith("COMMUNITY#")
        items, _ = self.dynamodb_controller.query_with_pagination(model_class, key_condition_expression)
        return items

    @log_and_handle_exceptions
    def add_owner(self, owner_item: Dict[str, Any]) -> None:
        """Adds an owner to a community.

        Args:
            owner_item (Dict[str, Any]): The owner item to add.
        """
        self.dynamodb_controller.put_item(owner_item)

    @log_and_handle_exceptions
    def remove_owner(self, model_class: Type[Model], community_id: str, user_id: str) -> None:
        """Removes an owner from a community.

        Args:
            model_class (Type[Model]): The model class of the owner.
            community_id (str): The ID of the community.
            user_id (str): The ID of the user to remove as owner.

        Raises:
            ValueError: If the community_id or user_id is invalid.
        """
        self._validate_model_class(model_class)
        self._validate_key(community_id, "Community ID")
        self._validate_key(user_id, "User ID")
        pk = f"COMMUNITY#{community_id}"
        sk = f"OWNER#{user_id}"
        self.dynamodb_controller.delete_item(model_class, pk, sk)

    @log_and_handle_exceptions
    def add_member(self, member_item: Dict[str, Any]) -> None:
        """Adds a member to a community.

        Args:
            member_item (Dict[str, Any]): The member item to add.
        """
        self.dynamodb_controller.put_item(member_item)

    @log_and_handle_exceptions
    def remove_member(self, model_class: Type[Model], community_id: str, user_id: str) -> None:
        """Removes a member from a community.

        Args:
            model_class (Type[Model]): The model class of the member.
            community_id (str): The ID of the community.
            user_id (str): The ID of the user to remove as member.

        Raises:
            ValueError: If the community_id or user_id is invalid.
        """
        self._validate_model_class(model_class)
        self._validate_key(community_id, "Community ID")
        self._validate_key(user_id, "User ID")
        pk = f"COMMUNITY#{community_id}"
        sk = f"MEMBER#{user_id}"
        self.dynamodb_controller.delete_item(model_class, pk, sk)
