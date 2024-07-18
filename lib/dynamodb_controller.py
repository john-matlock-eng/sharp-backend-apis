import logging
from functools import wraps
from pynamodb.exceptions import PynamoDBException
from pynamodb.models import Model
from typing import Type, List, Dict, Any, Optional, Tuple

class DynamoDBController:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def log_and_handle_exceptions(method):
        """
        Decorator for logging method calls and handling exceptions.
        """
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            try:
                self.logger.info(f"Calling {method.__name__} with args: {args}, kwargs: {kwargs}")
                result = method(self, *args, **kwargs)
                self.logger.info(f"{method.__name__} completed successfully")
                return result
            except PynamoDBException as e:
                self.logger.error(f"DynamoDB error in {method.__name__}: {e}")
                raise
            except Exception as e:
                self.logger.error(f"Unexpected error in {method.__name__}: {e}")
                raise
        return wrapper

    def _validate_model_class(self, model_class: Type[Model]) -> None:
        """
        Validate the model class.
        """
        if not issubclass(model_class, Model):
            raise ValueError(f"{model_class} is not a subclass of pynamodb.models.Model")

    def _validate_item(self, item: Model) -> None:
        """
        Validate the item.
        """
        if not isinstance(item, Model):
            raise ValueError("item must be an instance of pynamodb.models.Model")
        if item.table_name != self.table_name:
            raise ValueError(f"item's table name {item.table_name} does not match controller's table name {self.table_name}")

    def _validate_key(self, key: str, key_name: str) -> None:
        """
        Validate the key.
        """
        if not isinstance(key, str) or not key:
            raise ValueError(f"{key_name} must be a non-empty string")

    def _validate_update_data(self, update_data: Dict[str, Any]) -> None:
        """
        Validate the update data.
        """
        if not isinstance(update_data, dict) or not update_data:
            raise ValueError("update_data must be a non-empty dictionary")
        for key, value in update_data.items():
            if not isinstance(key, str) or not key:
                raise ValueError(f"update_data key {key} must be a non-empty string")
            if not isinstance(value, (str, int, float, list, dict, bool)):
                raise ValueError(f"update_data value for key {key} has an unsupported type {type(value)}")

    @log_and_handle_exceptions
    def put_item(self, item: Model) -> None:
        """
        Save an item to the DynamoDB table.

        :param item: The item to save.
        """
        self._validate_item(item)
        item.save()

    @log_and_handle_exceptions
    def get_item(self, model_class: Type[Model], pk: str, sk: str) -> Optional[Model]:
        """
        Retrieve an item from the DynamoDB table.

        :param model_class: The model class of the item.
        :param pk: The partition key of the item.
        :param sk: The sort key of the item.
        :return: The retrieved item or None if not found.
        """
        self._validate_model_class(model_class)
        self._validate_key(pk, "Partition key")
        self._validate_key(sk, "Sort key")
        
        try:
            return model_class.get(pk, sk)
        except model_class.DoesNotExist:
            self.logger.info("Item not found in DynamoDB table")
            return None

    @log_and_handle_exceptions
    def update_item(self, model_class: Type[Model], pk: str, sk: str, update_data: Dict[str, Any]) -> None:
        """
        Update an item in the DynamoDB table.

        :param model_class: The model class of the item.
        :param pk: The partition key of the item.
        :param sk: The sort key of the item.
        :param update_data: A dictionary of attributes to update.
        """
        self._validate_model_class(model_class)
        self._validate_key(pk, "Partition key")
        self._validate_key(sk, "Sort key")
        self._validate_update_data(update_data)
        
        item = model_class.get(pk, sk)
        for key, value in update_data.items():
            setattr(item, key, value)
        item.save()

    @log_and_handle_exceptions
    def delete_item(self, model_class: Type[Model], pk: str, sk: str) -> None:
        """
        Delete an item from the DynamoDB table.

        :param model_class: The model class of the item.
        :param pk: The partition key of the item.
        :param sk: The sort key of the item.
        """
        self._validate_model_class(model_class)
        self._validate_key(pk, "Partition key")
        self._validate_key(sk, "Sort key")
        
        item = model_class.get(pk, sk)
        item.delete()

    @log_and_handle_exceptions
    def query_with_pagination(self, model_class: Type[Model], key_condition_expression: Any, filter_expression: Optional[Any] = None, index_name: Optional[str] = None, limit: int = 20, last_evaluated_key: Optional[Dict[str, Any]] = None) -> Tuple[List[Model], Optional[Dict[str, Any]]]:
        """
        Query items in the DynamoDB table with pagination.

        :param model_class: The model class of the items.
        :param key_condition_expression: The key condition expression for the query.
        :param filter_expression: Optional filter expression for the query.
        :param index_name: Optional index name for the query.
        :param limit: The maximum number of items to retrieve.
        :param last_evaluated_key: The last evaluated key for pagination.
        :return: A tuple containing the list of retrieved items and the last evaluated key.
        """
        self._validate_model_class(model_class)
        if limit <= 0:
            raise ValueError("Limit must be a positive integer")

        query_params = {
            'KeyConditionExpression': key_condition_expression,
            'Limit': limit
        }
        if filter_expression:
            query_params['FilterExpression'] = filter_expression
        if index_name:
            query_params['IndexName'] = index_name
        if last_evaluated_key:
            query_params['ExclusiveStartKey'] = last_evaluated_key

        response = model_class.query(**query_params)
        items = list(response)
        last_evaluated_key = response.last_evaluated_key
        return items, last_evaluated_key

    @log_and_handle_exceptions
    def scan_with_pagination(self, model_class: Type[Model], filter_expression: Optional[Any] = None, limit: int = 20, last_evaluated_key: Optional[Dict[str, Any]] = None) -> Tuple[List[Model], Optional[Dict[str, Any]]]:
        """
        Scan items in the DynamoDB table with pagination.

        :param model_class: The model class of the items.
        :param filter_expression: Optional filter expression for the scan.
        :param limit: The maximum number of items to retrieve.
        :param last_evaluated_key: The last evaluated key for pagination.
        :return: A tuple containing the list of retrieved items and the last evaluated key.
        """
        self._validate_model_class(model_class)
        if limit <= 0:
            raise ValueError("Limit must be a positive integer")

        scan_params = {
            'Limit': limit
        }
        if filter_expression:
            scan_params['FilterExpression'] = filter_expression
        if last_evaluated_key:
            scan_params['ExclusiveStartKey'] = last_evaluated_key

        response = model_class.scan(**scan_params)
        items = list(response)
        last_evaluated_key = response.last_evaluated_key
        return items, last_evaluated_key

    @log_and_handle_exceptions
    def batch_write(self, items: List[Model]) -> None:
        """
        Perform a batch write of items to the DynamoDB table.

        :param items: The list of items to write.
        """
        if not items:
            raise ValueError("Items list cannot be empty")
        for item in items:
            self._validate_item(item)
        
        with items[0].__class__.batch_write() as batch:
            for item in items:
                batch.save(item)

    @log_and_handle_exceptions
    def batch_get(self, model_class: Type[Model], keys: List[Dict[str, Any]]) -> List[Model]:
        """
        Perform a batch get of items from the DynamoDB table.

        :param model_class: The model class of the items.
        :param keys: The list of keys of the items to retrieve.
        :return: A list of retrieved items.
        """
        self._validate_model_class(model_class)
        if not keys:
            raise ValueError("Keys list cannot be empty")
        for key in keys:
            if not isinstance(key, dict) or not all(isinstance(k, str) and v for k, v in key.items()):
                raise ValueError("Each key must be a dictionary with non-empty string keys and values")
        
        response = model_class.batch_get(keys)
        return list(response)
