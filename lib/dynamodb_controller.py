import boto3
from boto3.dynamodb.conditions import Key
import logging
from functools import wraps
from typing import Dict, Any, List, Optional, Tuple

class DynamoDBController:
    def __init__(self, table_name: str, region_name: str = 'us-east-2'):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table(table_name)
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
    def put_item(self, item: Dict[str, Any]) -> None:
        """Save an item to the DynamoDB table.

        Args:
            item (Dict[str, Any]): The item to save.
        """
        self.table.put_item(Item=item)

    @log_and_handle_exceptions
    def get_item(self, pk: str, sk: str) -> Optional[Dict[str, Any]]:
        """Retrieve an item from the DynamoDB table.

        Args:
            pk (str): The partition key of the item.
            sk (str): The sort key of the item.

        Returns:
            Optional[Dict[str, Any]]: The retrieved item or None if not found.
        """
        response = self.table.get_item(
            Key={
                'PK': pk,
                'SK': sk
            }
        )
        return response.get('Item')

    @log_and_handle_exceptions
    def update_item(self, pk: str, sk: str, update_data: Dict[str, Any]) -> None:
        """Update an item in the DynamoDB table.

        Args:
            pk (str): The partition key of the item.
            sk (str): The sort key of the item.
            update_data (Dict[str, Any]): A dictionary of attributes to update.
        """
        update_expr = "set " + ", ".join(f"{k}=:{k}" for k in update_data.keys())
        expr_attr_values = {f":{k}": v for k, v in update_data.items()}
        self.table.update_item(
            Key={
                'PK': pk,
                'SK': sk
            },
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_attr_values
        )

    @log_and_handle_exceptions
    def delete_item(self, pk: str, sk: str) -> None:
        """Delete an item from the DynamoDB table.

        Args:
            pk (str): The partition key of the item.
            sk (str): The sort key of the item.
        """
        self.table.delete_item(
            Key={
                'PK': pk,
                'SK': sk
            }
        )

    @log_and_handle_exceptions
    def query_with_pagination(self, key_condition: Key, filter_condition: Optional[Any] = None, index_name: Optional[str] = None, limit: int = 20, last_evaluated_key: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Query items in the DynamoDB table with pagination.

        Args:
            key_condition (Key): The key condition for the query.
            filter_condition (Optional[Any]): Optional filter condition for the query.
            index_name (Optional[str]): Optional index name for the query.
            limit (int): The maximum number of items to retrieve.
            last_evaluated_key (Optional[Dict[str, Any]]): The last evaluated key for pagination.

        Returns:
            Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]: A tuple containing the list of retrieved items and the last evaluated key.
        """
        query_params = {
            'KeyConditionExpression': key_condition,
            'Limit': limit
        }
        if filter_condition:
            query_params['FilterExpression'] = filter_condition
        if index_name:
            query_params['IndexName'] = index_name
        if last_evaluated_key:
            query_params['ExclusiveStartKey'] = last_evaluated_key

        response = self.table.query(**query_params)

        items = response.get('Items', [])
        last_evaluated_key = response.get('LastEvaluatedKey')
        return items, last_evaluated_key
