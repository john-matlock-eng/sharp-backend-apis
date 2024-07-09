provider "aws" {
  region = var.aws_region
}

data "aws_ecr_repository" "api_ecr_repository" {
  name = "${var.api_name}"
}

data "aws_iam_role" "api_lambda_exec" {
  name = "api_lambda_exec"
}

resource "aws_lambda_function" "lambda" {
  function_name = var.api_name
  package_type = "Image"
  image_uri     = "${data.aws_ecr_repository.api_ecr_repository.repository_url}:${var.image_tag}"
  role          = data.aws_iam_role.api_lambda_exec.arn
  architectures = ["x86_64"]
  memory_size   = var.memory_size
  timeout       = var.timeout
}
