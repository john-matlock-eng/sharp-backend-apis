import os
from services.user_service import UserService
from lib.dynamodb_controller import DynamoDBController
from models.user_schema import UserCreate

def handler(event, context):
    user_sub = event['request']['userAttributes']['sub']
    moniker = event['request']['userAttributes'].get('custom:moniker')
    user: UserCreate = UserCreate(user_id=user_sub, moniker=moniker)
    table_name = os.getenv('TABLE_NAME', 'sharp_app_data')
    dynamodb_controller = DynamoDBController(table_name)
    user_service = UserService(dynamodb_controller)
    
    user_service.create_user(user)
    
    return event
