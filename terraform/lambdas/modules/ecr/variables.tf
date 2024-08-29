variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "us-east-2"
}

variable "lambda_name" {
  description = "Name of the Lambda to be deployed, used for Lambda function and ECR repository names"
  type        = string
  default     = ""
}

