import os
from services.user_service import UserService
from lib.dynamodb_controller import DynamoDBController
from models.user_schema import UserCreate
from datetime import datetime, timezone

def handler(event, context):
    user_sub = event['request']['userAttributes']['sub']
    name = event['request']['userAttributes'].get('custom:moniker', '')
    joined_at = int(datetime.now(timezone.utc).timestamp())

    user = UserCreate(
        user_id=user_sub,
        name=name,
        joined_at=joined_at
    )

    table_name = os.getenv('TABLE_NAME', 'sharp_app_data')
    dynamodb_controller = DynamoDBController(table_name)
    user_service = UserService(dynamodb_controller)
    
    user_service.create_user(user)
    
    return event
