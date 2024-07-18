from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, ListAttribute

class CommunityModel(Model):
    """
    A PynamoDB model representing a community.
    """
    class Meta:
        table_name = 'sharp_app_data'
        region = 'us-east-2'

    PK = UnicodeAttribute(hash_key=True)
    SK = UnicodeAttribute(range_key=True)
    community_id = UnicodeAttribute()
    name = UnicodeAttribute()
    description = UnicodeAttribute()
    owner_ids = ListAttribute(of=UnicodeAttribute)
    members = ListAttribute(of=UnicodeAttribute)
    keywords = ListAttribute(of=UnicodeAttribute)
