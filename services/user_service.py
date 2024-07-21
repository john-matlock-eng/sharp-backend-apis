import logging
from functools import wraps
from app.lib.dynamodb_controller import DynamoDBController
from boto3.dynamodb.conditions import Key
from app.models.user_model import UserModel

class UserService:
    def __init__(self, table_name):
        self.dynamodb_controller = DynamoDBController(table_name)

    def create_user(self, user_id, name, email, joined_at):
        user = UserModel(
            PK=f'USER#{user_id}',
            SK='PROFILE',
            EntityType='User',
            Name=name,
            Email=email,
            JoinedAt=joined_at
        )
        return self.dynamodb_controller.put_item(user.dict(by_alias=True))

    def get_user(self, user_id):
        return self.dynamodb_controller.get_item(f'USER#{user_id}', 'PROFILE')

    def list_communities_for_user(self, user_id):
        key_condition = Key('PK').eq(f'USER#{user_id}') & Key('SK').begins_with('COMMUNITY#')
        return self.dynamodb_controller.query_with_pagination(key_condition)
