provider "aws" {
  region = var.aws_region
}

data "aws_ecr_repository" "api_ecr_repository" {
  name = var.api_name
}

resource "aws_iam_role" "lambda_exec_role" {
  name               = "${var.api_name}_lambda_exec"
  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Effect": "Allow",
        "Sid": ""
      }
    ]
  }
  EOF
}

resource "aws_iam_policy_attachment" "api_lambda_policy_attachment" {
  name       = "cognito_post_confirmation_lambda_exec_attachment"
  roles      = [aws_iam_role.lambda_exec_role.name]
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_lambda_function" "lambda" {
  function_name = var.api_name
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.api_ecr_repository.repository_url}:${var.image_tag}"
  role          = aws_iam_role.lambda_exec_role.arn
  architectures = ["x86_64"]
  memory_size   = var.memory_size
  timeout       = var.timeout
}
