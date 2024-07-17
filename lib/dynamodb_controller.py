import boto3
import logging
from botocore.exceptions import ClientError

class DynamoDBController:
    def __init__(self, table_name):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        self.logger = logging.getLogger(__name__)

    def put_item(self, item):
        try:
            self.logger.info(f"Putting item into DynamoDB table: {item}")
            self.table.put_item(Item=item)
            self.logger.info("Item successfully put into DynamoDB table")
        except ClientError as e:
            self.logger.error(f"DynamoDB client error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while putting item into DynamoDB table: {e}")
            raise

    def get_item(self, key):
        try:
            self.logger.info(f"Getting item from DynamoDB table with key: {key}")
            response = self.table.get_item(Key=key)
            item = response.get('Item')
            if item:
                self.logger.info("Item successfully retrieved from DynamoDB table")
            else:
                self.logger.info("Item not found in DynamoDB table")
            return item
        except ClientError as e:
            self.logger.error(f"DynamoDB client error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while getting item from DynamoDB table: {e}")
            raise

    def update_item(self, key, update_expression, expression_attribute_values):
        try:
            self.logger.info(f"Updating item in DynamoDB table with key: {key}")
            self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            self.logger.info("Item successfully updated in DynamoDB table")
        except ClientError as e:
            self.logger.error(f"DynamoDB client error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while updating item in DynamoDB table: {e}")
            raise

    def delete_item(self, key):
        try:
            self.logger.info(f"Deleting item from DynamoDB table with key: {key}")
            self.table.delete_item(Key=key)
            self.logger.info("Item successfully deleted from DynamoDB table")
        except ClientError as e:
            self.logger.error(f"DynamoDB client error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while deleting item from DynamoDB table: {e}")
            raise

    def scan_table(self):
        try:
            self.logger.info("Scanning DynamoDB table for all items")
            response = self.table.scan()
            self.logger.info("Table scan completed successfully")
            return response
        except ClientError as e:
            self.logger.error(f"DynamoDB client error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while scanning DynamoDB table: {e}")
            raise
