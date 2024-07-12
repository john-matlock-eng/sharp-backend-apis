resource "aws_dynamodb_table" "sharp_app_data" {
  name         = "sharp_app_data"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "PK"
  range_key    = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  attribute {
    name = "Type"
    type = "S"
  }

  attribute {
    name = "CreatedAt"
    type = "N"
  }

  attribute {
    name = "CreatedBy"
    type = "S"
  }

  attribute {
    name = "KnowledgeSpaceId"
    type = "S"
  }

  global_secondary_index {
    name            = "TypeIndex"
    hash_key        = "Type"
    range_key       = "CreatedAt"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "UserContentIndex"
    hash_key        = "CreatedBy"
    range_key       = "Type"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "KnowledgeSpaceIndex"
    hash_key        = "KnowledgeSpaceId"
    range_key       = "Type"
    projection_type = "ALL"
  }

  tags = {
    Environment = "production"
    Name        = "sharp_app_data"
  }
}
