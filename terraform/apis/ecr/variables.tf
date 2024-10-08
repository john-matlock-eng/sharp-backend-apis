variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "us-east-2"
}

variable "api_name" {
  description = "Name of the API to be deployed, used for Lambda function and ECR repository names"
  type        = string
  default     = ""
}
