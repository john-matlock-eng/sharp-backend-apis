variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "us-east-2"
}

variable "image_tag" {
  description = "Tag for the Docker image"
  type        = string
}
