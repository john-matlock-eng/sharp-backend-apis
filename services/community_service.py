import logging
from botocore.exceptions import ClientError

class CommunityService:
    def __init__(self, dynamodb_controller):
        self.dynamodb_controller = dynamodb_controller
        self.logger = logging.getLogger(__name__)

    def create_community(self, community_data):
        try:
            self.logger.info("Creating community")
            self.dynamodb_controller.put_item(community_data)
            self.logger.info("Community created successfully")
        except ClientError as e:
            self.logger.error(f"DynamoDB client error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while creating community: {e}")
            raise

    def get_community(self, community_id):
        try:
            self.logger.info(f"Fetching community with ID: {community_id}")
            key = {"community_id": community_id}
            return self.dynamodb_controller.get_item(key)
        except ClientError as e:
            self.logger.error(f"DynamoDB client error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while getting community: {e}")
            raise

    def update_community(self, community_id, update_data):
        try:
            self.logger.info(f"Updating community with ID: {community_id}")
            key = {"community_id": community_id}
            update_expression = "set " + ", ".join(f"{k}=:{k}" for k in update_data.keys())
            expression_attribute_values = {f":{k}": v for k, v in update_data.items()}
            self.dynamodb_controller.update_item(key, update_expression, expression_attribute_values)
            self.logger.info("Community updated successfully")
        except ClientError as e:
            self.logger.error(f"DynamoDB client error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while updating community: {e}")
            raise

    def delete_community(self, community_id):
        try:
            self.logger.info(f"Deleting community with ID: {community_id}")
            key = {"community_id": community_id}
            self.dynamodb_controller.delete_item(key)
            self.logger.info("Community deleted successfully")
        except ClientError as e:
            self.logger.error(f"DynamoDB client error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while deleting community: {e}")
            raise
