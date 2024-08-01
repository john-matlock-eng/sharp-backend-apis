import logging
from typing import Dict, Any, List
from boto3.dynamodb.conditions import Key
from app.lib.dynamodb_controller import DynamoDBController
from app.models.user_schema import UserCreate, UserUpdate

class UserService:
    def __init__(self, dynamodb_controller: DynamoDBController):
        self.dynamodb_controller = dynamodb_controller
        self.logger = logging.getLogger(__name__)

    def create_user(self, user: UserCreate) -> None:
        item = {
            'PK': "USER",
            'SK': f'USER#{user.user_id}',
            'EntityType': 'User',
            'CreatedAt': user.joined_at,
            'user_id': str(user.user_id),
            'name': user.name,
        }
        self.dynamodb_controller.put_item(item)

    def get_user(self, user_id: str) -> Dict[str, Any]:
        return self.dynamodb_controller.get_item(f'USER#{user_id}', 'PROFILE')

    def update_user(self, user_id: str, update_data: UserUpdate) -> None:
        update_dict = update_data.dict(exclude_unset=True)
        self.dynamodb_controller.update_item(f'USER#{user_id}', 'PROFILE', update_dict)

    def delete_user(self, user_id: str) -> None:
        self.dynamodb_controller.delete_item(f'USER#{user_id}', 'PROFILE')

    def list_users(self) -> List[Dict[str, Any]]:
        partition_key = Key('PK').begins_with('USER#')
        sort_key_condition = Key('SK').eq('PROFILE')
        return self.dynamodb_controller.query_with_pagination(partition_key, sort_key_condition)[0]

    def list_communities_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        partition_key = Key('PK').eq(f'USER#{user_id}')
        sort_key_condition = Key('SK').begins_with('COMMUNITY#')
        return self.dynamodb_controller.query_with_pagination(partition_key, sort_key_condition)[0]

