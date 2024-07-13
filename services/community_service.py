class CommunityService:
    def __init__(self, dynamodb_controller):
        self.dynamodb_controller = dynamodb_controller

    def get_community(self, community_id):
        return self.dynamodb_controller.get_item(f'COMMUNITY#{community_id}', f'COMMUNITY#{community_id}')

    def create_community(self, community_id, name):
        item = {
            'PK': f'COMMUNITY#{community_id}',
            'SK': f'COMMUNITY#{community_id}',
            'DataType': 'COMMUNITY',
            'Name': name
        }
        self.dynamodb_controller.put_item(item)

    def update_community(self, community_id, name=None):
        update_expression = "SET"
        expression_attribute_values = {}
        if name:
            update_expression += " Name = :n,"
            expression_attribute_values[':n'] = name
        update_expression = update_expression.rstrip(',')

        self.dynamodb_controller.update_item(
            f'COMMUNITY#{community_id}', f'COMMUNITY#{community_id}', update_expression, expression_attribute_values
        )

    def delete_community(self, community_id):
        self.dynamodb_controller.delete_item(f'COMMUNITY#{community_id}', f'COMMUNITY#{community_id}')
    
    def list_communities(self):
        filter_expression = "DataType = :community"
        expression_attribute_values = {
            ":community": "COMMUNITY"
        }
        return self.dynamodb_controller.scan(filter_expression, expression_attribute_values)
