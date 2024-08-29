variable "aws_region" {
  description = "The AWS region to create resources in"
  type        = string
  default     = "us-east-2"
}

variable "lambda_name" {
  description = "The name of the Lambda function"
  type        = string
}

variable "image_tag" {
  description = "The Docker image tag for the Lambda function"
  type        = string
}

variable "dynamodb_table_name" {
  description = "The DynamoDB table name the Lambda will interact with"
  type        = string
}

variable "architecture" {
  description = "The architecture for the Lambda function (e.g., arm64, x86_64)"
  type        = string
  default     = "x86_64"
}

variable "memory_size" {
  description = "The amount of memory allocated to the Lambda function"
  type        = number
  default     = 256
}

variable "timeout" {
  description = "The timeout for the Lambda function"
  type        = number
  default     = 30
}

variable "environment_variables" {
  description = "Environment variables for the Lambda function"
  type        = map(string)
  default     = {}
}

variable "sqs_arn" {
  description = "The ARN of the SQS queue to trigger the Lambda function"
  type        = string
  default     = ""
}

variable "openai_api_key" {
  description = "The OpenAI API key for the Lambda function"
  type        = string
}
