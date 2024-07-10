import boto3
from botocore.exceptions import ClientError

class DynamoDBController:
    def __init__(self, table_name):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def get_item(self, pk, sk):
        try:
            response = self.table.get_item(Key={'PK': pk, 'SK': sk})
            return response.get('Item')
        except ClientError as e:
            print(e.response['Error']['Message'])
            return None

    def put_item(self, item):
        try:
            self.table.put_item(Item=item)
        except ClientError as e:
            print(e.response['Error']['Message'])
            return None

    def update_item(self, pk, sk, update_expression, expression_attribute_values):
        try:
            self.table.update_item(
                Key={'PK': pk, 'SK': sk},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return None

    def delete_item(self, pk, sk):
        try:
            self.table.delete_item(Key={'PK': pk, 'SK': sk})
        except ClientError as e:
            print(e.response['Error']['Message'])
            return None
