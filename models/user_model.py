from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute

class UserModel(Model):
    """
    A PynamoDB model representing a user.
    """
    class Meta:
        table_name = 'sharp_app_data'
        region = 'us-east-2'

    PK = UnicodeAttribute(hash_key=True)
    SK = UnicodeAttribute(range_key=True)
    DataType = UnicodeAttribute()
    Moniker = UnicodeAttribute()
