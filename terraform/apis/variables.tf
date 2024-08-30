variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "us-east-2"
}

variable "image_tag" {
  description = "Tag for the Docker image"
  type        = string
}

variable "api_name" {
  description = "Name of the API to be deployed, used for Lambda function and ECR repository names"
  type        = string
  default     = ""
}

variable "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  type        = string
  default     = ""
}

variable "cognito_user_pool_client_id" {
  description = "Cognito User Pool Client ID"
  type        = string
  default     = ""
}

variable "knowledge_source_url_initial_ingestion_queue" {
  description = "The SQS URL for the knowledge source ingestion queue"
  type        = string
}
