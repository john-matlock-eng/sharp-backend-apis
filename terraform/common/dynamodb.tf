resource "aws_dynamodb_table" "sharp_app_data" {
  name           = "sharp_app_data"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "PK"
  range_key      = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  attribute {
    name = "UserId"
    type = "S"
  }

  attribute {
    name = "KnowledgeSpaceId"
    type = "S"
  }

  attribute {
    name = "CreatedAt"
    type = "S"
  }

  global_secondary_index {
    name               = "UserId-Index"
    hash_key           = "UserId"
    range_key          = "CreatedAt"
    projection_type    = "ALL"
  }

  global_secondary_index {
    name               = "KnowledgeSpaceId-Index"
    hash_key           = "KnowledgeSpaceId"
    range_key          = "SK"
    projection_type    = "ALL"
  }

  tags = {
    Environment = "production"
    Name        = "sharp_app_data"
  }
}
