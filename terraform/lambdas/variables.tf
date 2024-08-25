variable "aws_region" {
  description = "The AWS region to create resources in"
  type        = string
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
}

variable "memory_size" {
  description = "The amount of memory allocated to the Lambda function"
  type        = number
}

variable "timeout" {
  description = "The timeout for the Lambda function"
  type        = number
}

variable "environment_variables" {
  description = "Environment variables for the Lambda function"
  type        = map(string)
}

variable "sqs_arn" {
  description = "The ARN of the SQS queue to trigger the Lambda function"
  type        = string
}
