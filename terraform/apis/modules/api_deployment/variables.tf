variable "aws_region" {
  description = "The AWS region to create resources in"
  type        = string
  default     = "us-east-2"
}

variable "folder_path" {
  description = "Path to the folder containing the Docker configuration"
  type        = string
  default     = ""
}

variable "api_name" {
  description = "Name of the API to be deployed, used for Lambda function and ECR repository names"
  type        = string
  default     = ""
}

variable "lambda_handler" {
  description = "Lambda function handler"
  type        = string
  default     = "lambda.handler"
}

variable "runtime" {
  description = "Lambda runtime environment"
  type        = string
  default     = "python3.12"
}

variable "image_tag" {
  description = "Tag for the Docker image"
  type        = string
  default     = "latest"
}

variable "build_platform" {
  description = "Docker build platform (e.g., linux/arm64)"
  type        = string
  default     = "linux/arm64"
}

variable "memory_size" {
  description = "Lambda function memory size"
  type        = number
  default     = 256
}

variable "timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 30
}
