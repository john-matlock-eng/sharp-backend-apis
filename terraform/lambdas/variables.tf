variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "us-east-2"
}

variable "dynamodb_table_name" {
  description = "The name of the DynamoDB table"
  type        = string
  default     = "sharp_app_data"
}

variable "image_tag" {
  description = "Tag for the Docker image"
  type        = string
}
