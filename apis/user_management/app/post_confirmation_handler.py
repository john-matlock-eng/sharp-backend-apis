import json
import os
from app.user_service import UserService
from lib.dynamodb_controller import DynamoDBController

def lambda_handler(event, context):
    user_sub = event['request']['userAttributes']['sub']
    moniker = event['request']['userAttributes'].get('custom:moniker')
    
    table_name = os.getenv('TABLE_NAME', 'sharp_app_data')
    dynamodb_controller = DynamoDBController(table_name)
    user_service = UserService(dynamodb_controller)
    
    user_service.create_user(user_sub, moniker)
    
    return event
