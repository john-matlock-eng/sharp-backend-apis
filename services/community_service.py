import logging
from fastapi import HTTPException
from functools import wraps
from typing import Dict, Any, List
from boto3.dynamodb.conditions import Key
from app.lib.dynamodb_controller import DynamoDBController
from app.models.community_member_model import CommunityMemberModel
from app.models.community_schema import CommunityCreate


class CommunityService:
    def __init__(self, dynamodb_controller: DynamoDBController):
        self.dynamodb_controller = dynamodb_controller

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

    def get_community(self, community_id: str) -> Dict[str, Any]:
        return self.dynamodb_controller.get_item('COMMUNITY', f'COMMUNITY#{community_id}')

    def update_community(self, community_id: str, update_data: Dict[str, Any]) -> None:
        self.dynamodb_controller.update_item('COMMUNITY', f'COMMUNITY#{community_id}', update_data)

    def delete_community(self, community_id: str) -> None:
        self.dynamodb_controller.delete_item('COMMUNITY', f'COMMUNITY#{community_id}')

    def add_owner(self, community_id: str, owner_id: str) -> None:
        self.dynamodb_controller.update_item(f'COMMUNITY#{community_id}', 'DETAILS', {'OwnerID': owner_id})

    def remove_owner(self, community_id: str, user_id: str) -> None:
        # Implement the logic to remove owner
        pass

    def add_member(self, community_id: str, member: CommunityMemberModel) -> None:
        self.dynamodb_controller.put_item(member.dict(by_alias=True))

    def remove_member(self, community_id: str, user_id: str) -> None:
        self.dynamodb_controller.delete_item(f'COMMUNITY#{community_id}', f'MEMBER#{user_id}')

    def list_communities(self) -> List[Dict[str, Any]]:
        partition_key = Key('PK').eq('COMMUNITY')
        sort_key_condition = Key('SK').begins_with('COMMUNITY#')
        return self.dynamodb_controller.query_with_pagination(partition_key, sort_key_condition)[0]

    def is_user_owner(self, community_id: str, user_id: str) -> bool:
        community = self.get_community(community_id)
        if not community:
            raise HTTPException(status_code=404, detail="Community not found")
        return user_id in community['owner_ids']

    def assert_user_is_owner(self, community_id: str, user_id: str):
        if not self.is_user_owner(community_id, user_id):
            raise HTTPException(status_code=403, detail="User is not authorized for this action")