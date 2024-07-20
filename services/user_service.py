import logging
from functools import wraps
from app.lib.dynamodb_controller import DynamoDBController
from app.models.user_model import UserModel
from app.models.user_schema import UserCreate, UserUpdate

class UserService:
    """Service class for managing user operations."""

    def __init__(self, dynamodb_controller: DynamoDBController):
        """Initializes the UserService with a DynamoDBController.

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
    def get_user(self, user_id: str) -> UserModel:
        """Fetches a user by its ID.

        Args:
            user_id (str): The ID of the user to fetch.

        Returns:
            UserModel: The fetched user item.
        """
        pk = f'USER#{user_id}'
        sk = f'USER#{user_id}'
        return self.dynamodb_controller.get_item(pk, sk)

    @log_and_handle_exceptions
    def create_user(self, user: UserCreate) -> None:
        """Creates a new user.

        Args:
            user (UserCreate): The user data to create.
        """
        new_user = {
            "PK": f'USER#{user.user_id}',
            "SK": f'USER#{user.user_id}',
            "DataType": 'USER',
            "Moniker": user.moniker
        }
        self.dynamodb_controller.put_item(UserModel(**new_user))

    @log_and_handle_exceptions
    def update_user(self, user_id: str, user_update: UserUpdate) -> None:
        """Updates a user by its ID.

        Args:
            user_id (str): The ID of the user to update.
            user_update (UserUpdate): The data to update in the user.
        """
        pk = f'USER#{user_id}'
        sk = f'USER#{user_id}'
        update_dict = user_update.dict()
        self.dynamodb_controller.update_item(UserModel, pk, sk, update_dict)

    @log_and_handle_exceptions
    def delete_user(self, user_id: str) -> None:
        """Deletes a user by its ID.

        Args:
            user_id (str): The ID of the user to delete.
        """
        pk = f'USER#{user_id}'
        sk = f'USER#{user_id}'
        self.dynamodb_controller.delete_item(UserModel, pk, sk)
