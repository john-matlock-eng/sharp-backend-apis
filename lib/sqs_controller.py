import boto3
import logging
from botocore.exceptions import BotoCoreError, ClientError
from typing import Dict, Any, List, Optional
from app.lib.logging import log_and_handle_exceptions

class SQSController:
    def __init__(self, queue_url: str, region_name: str = 'us-east-2'):
        self.queue_url = queue_url
        self.region_name = region_name
        self.session = boto3.Session(region_name=region_name)
        self.sqs = self.session.client('sqs')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    @log_and_handle_exceptions
    def send_message(self, message_body: str, message_attributes: Optional[Dict[str, Any]] = None) -> None:
        """Send a message to the SQS queue.

        Args:
            message_body (str): The body of the message to send.
            message_attributes (Optional[Dict[str, Any]]): Optional attributes for the message.
        """
        send_params = {
            'QueueUrl': self.queue_url,
            'MessageBody': message_body
        }
        if message_attributes:
            send_params['MessageAttributes'] = message_attributes

        self.sqs.send_message(**send_params)

    @log_and_handle_exceptions
    def receive_messages(self, max_number: int = 1, wait_time_seconds: int = 0, visibility_timeout: int = 30) -> List[Dict[str, Any]]:
        """Receive messages from the SQS queue.

        Args:
            max_number (int): The maximum number of messages to return.
            wait_time_seconds (int): The duration (in seconds) for which the call waits for a message to arrive.
            visibility_timeout (int): The visibility timeout for the messages.

        Returns:
            List[Dict[str, Any]]: A list of messages retrieved from the queue.
        """
        receive_params = {
            'QueueUrl': self.queue_url,
            'MaxNumberOfMessages': max_number,
            'WaitTimeSeconds': wait_time_seconds,
            'VisibilityTimeout': visibility_timeout
        }
        response = self.sqs.receive_message(**receive_params)
        messages = response.get('Messages', [])
        return messages

    @log_and_handle_exceptions
    def delete_message(self, receipt_handle: str) -> None:
        """Delete a message from the SQS queue.

        Args:
            receipt_handle (str): The receipt handle associated with the message.
        """
        self.sqs.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle
        )
