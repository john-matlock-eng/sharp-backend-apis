import logging
import os
import asyncio
from functools import wraps
from typing import Dict, Any, List

from fastapi import HTTPException
from boto3.dynamodb.conditions import Key

from app.lib.dynamodb_controller import DynamoDBController
from app.lib.logging import log_and_handle_exceptions
from app.models.community_schema import CommunityCreate
from app.models.community_member_schema import CommunityMemberModel


class CommunityService:
    def __init__(self, dynamodb_controller: DynamoDBController):
        self.dynamodb_controller = dynamodb_controller
        self.logger = logging.getLogger(__name__)

    @log_and_handle_exceptions
    def create_community(self, community: CommunityCreate) -> None:
        item = {
            'PK': 'COMMUNITY',
            'SK': f'COMMUNITY#{community.community_id}',
            'EntityType': 'Community',
            'CreatedAt': community.created_at,
            'community_id': str(community.community_id),
            'community_name': community.community_name,
            'description': community.description,
            'members': [str(member) for member in community.members],
            'keywords': community.keywords,
            'owner_ids': [str(owner_id) for owner_id in community.owner_ids],
        }
        self.dynamodb_controller.put_item(item)

    @log_and_handle_exceptions
    def get_community(self, community_id: str) -> Dict[str, Any]:
        return self.dynamodb_controller.get_item('COMMUNITY', f'COMMUNITY#{community_id}')

    @log_and_handle_exceptions
    def update_community(self, community_id: str, update_data: Dict[str, Any]) -> None:
        self.dynamodb_controller.update_item('COMMUNITY', f'COMMUNITY#{community_id}', update_data)

    @log_and_handle_exceptions
    def delete_community(self, community_id: str) -> None:
        self.dynamodb_controller.delete_item('COMMUNITY', f'COMMUNITY#{community_id}')

    @log_and_handle_exceptions
    def is_user_owner(self, community_id: str, user_id: str) -> bool:
        community = self.get_community(community_id)
        if not community:
            raise HTTPException(status_code=404, detail="Community not found")
        return user_id in community['owner_ids']

    @log_and_handle_exceptions
    def assert_user_is_owner(self, community_id: str, user_id: str):
        if not self.is_user_owner(community_id, user_id):
            raise HTTPException(status_code=403, detail="User is not authorized for this action")

    @log_and_handle_exceptions
    def is_user_member(self, community_id: str, user_id: str) -> bool:
        self.logger.info(f"Checking if user {user_id} is a member of community {community_id}")
        community = self.get_community(community_id)
        if not community:
            raise HTTPException(status_code=404, detail="Community not found")
        return user_id in community['members']

    @log_and_handle_exceptions
    def assert_user_is_member(self, community_id: str, user_id: str):
        if not self.is_user_member(community_id, user_id):
            raise HTTPException(status_code=403, detail="User is not authorized to view this resource")

    @log_and_handle_exceptions
    def add_owner(self, community_id: str, owner_id: str) -> None:
        self.dynamodb_controller.update_item(f'COMMUNITY#{community_id}', 'DETAILS', {'OwnerID': owner_id})

    @log_and_handle_exceptions
    def remove_owner(self, community_id: str, user_id: str) -> None:
        # Implement the logic to remove owner
        pass

    @log_and_handle_exceptions
    def add_member(self, community_id: str, member: CommunityMemberModel) -> None:
        self.dynamodb_controller.put_item(member.dict(by_alias=True))

    @log_and_handle_exceptions
    def remove_member(self, community_id: str, user_id: str) -> None:
        self.dynamodb_controller.delete_item(f'COMMUNITY#{community_id}', f'MEMBER#{user_id}')

    @log_and_handle_exceptions
    def list_communities(self) -> List[Dict[str, Any]]:
        partition_key = Key('PK').eq('COMMUNITY')
        sort_key_condition = Key('SK').begins_with('COMMUNITY#')
        return self.dynamodb_controller.query_with_pagination(partition_key, sort_key_condition)[0]

def requires_owner(community_id_param: str):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            community_id = kwargs.get(community_id_param)
            current_user = kwargs.get('current_user')
            community_service: CommunityService = kwargs.get('community_service')

            if not community_service.is_user_owner(community_id, current_user['sub']):
                raise HTTPException(status_code=403, detail="User is not authorized for this action")

            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            community_id = kwargs.get(community_id_param)
            current_user = kwargs.get('current_user')
            community_service: CommunityService = kwargs.get('community_service')

            if not community_service.is_user_owner(community_id, current_user['sub']):
                raise HTTPException(status_code=403, detail="User is not authorized for this action")

            return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

def requires_member(community_id_param: str):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            community_id = kwargs.get(community_id_param)
            current_user = kwargs.get('current_user')
            community_service: CommunityService = kwargs.get('community_service')

            if not community_service.is_user_member(community_id, current_user['sub']):
                raise HTTPException(status_code=403, detail="User is not authorized to view this resource")

            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            community_id = kwargs.get(community_id_param)
            current_user = kwargs.get('current_user')
            community_service: CommunityService = kwargs.get('community_service')

            if not community_service.is_user_member(community_id, current_user['sub']):
                raise HTTPException(status_code=403, detail="User is not authorized to view this resource")

            return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

def requires_quiz_owner():
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            quiz_id = kwargs.get('quiz_id')
            current_user = kwargs.get('current_user')
            quiz_service = kwargs.get('quiz_service')

            quiz_metadata = await quiz_service.get_quiz_metadata(quiz_id)
            if not quiz_metadata:
                raise HTTPException(status_code=404, detail="Quiz not found")

            if current_user['sub'] not in quiz_metadata['owner_ids']:
                raise HTTPException(status_code=403, detail="User is not authorized for this action")

            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            quiz_id = kwargs.get('quiz_id')
            current_user = kwargs.get('current_user')
            quiz_service = kwargs.get('quiz_service')

            quiz_metadata = quiz_service.get_quiz_metadata(quiz_id)
            if not quiz_metadata:
                raise HTTPException(status_code=404, detail="Quiz not found")

            if current_user['sub'] not in quiz_metadata['owner_ids']:
                raise HTTPException(status_code=403, detail="User is not authorized for this action")

            return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

def get_community_service() -> CommunityService:
    table_name = os.getenv('TABLE_NAME', 'sharp_app_data')
    dynamodb_controller = DynamoDBController(table_name)
    return CommunityService(dynamodb_controller)
