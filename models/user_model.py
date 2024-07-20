from pydantic import BaseModel, Field

class UserModel(BaseModel):
    """
    A Pydantic model representing a user.
    """
    PK: str = Field(..., regex=r'^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$', description="Primary Key, a valid UUID")
    SK: str = Field(..., regex=r'^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$', description="Sort Key, a valid UUID")
    DataType: str
    Moniker: str

    class Config:
        schema_extra = {
            "example": {
                "PK": "123e4567-e89b-12d3-a456-426614174000",
                "SK": "123e4567-e89b-12d3-a456-426614174001",
                "DataType": "example_type",
                "Moniker": "example_moniker"
            }
        }
        orm_mode = True
        allow_population_by_field_name = True
