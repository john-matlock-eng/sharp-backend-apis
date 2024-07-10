from lib.dynamodb_controller import DynamoDBController

class UserService:
    def __init__(self, dynamodb_controller):
        self.dynamodb_controller = dynamodb_controller

    def get_user(self, user_id):
        return self.dynamodb_controller.get_item(f'USER#{user_id}', f'USER#{user_id}')

    def create_user(self, user_id, moniker):
        item = {
            'PK': f'USER#{user_id}',
            'SK': f'USER#{user_id}',
            'DataType': 'USER',
            'Moniker': moniker
        }
        self.dynamodb_controller.put_item(item)

    def update_user(self, user_id, moniker=None):
        update_expression = "SET"
        expression_attribute_values = {}
        if moniker:
            update_expression += " Moniker = :m,"
            expression_attribute_values[':m'] = moniker
        update_expression = update_expression.rstrip(',')

        self.dynamodb_controller.update_item(
            f'USER#{user_id}', f'USER#{user_id}', update_expression, expression_attribute_values
        )

    def delete_user(self, user_id):
        self.dynamodb_controller.delete_item(f'USER#{user_id}', f'USER#{user_id}')
