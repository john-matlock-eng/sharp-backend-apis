provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

data "aws_ecr_repository" "repo" {
  name = var.lambda_name
}


variable "default_environment_variables" {
  description = "Default environment variables for all Lambdas"
  type        = map(string)
  default = {
    "OPENAI_API_KEY" = var.openai_api_key
  }
}

resource "aws_iam_role" "lambda_exec_role" {
  name               = "${var.lambda_name}_exec_role"
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

resource "aws_iam_policy" "lambda_logging" {
  name        = "${var.lambda_name}_logging_policy"
  description = "IAM policy for Lambda logging"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ],
        Resource = "arn:aws:logs:*:*:*"
      },
    ]
  })
}

resource "aws_iam_policy" "lambda_dynamodb" {
  name        = "${var.lambda_name}_dynamodb_policy"
  description = "IAM policy for Lambda to interact with DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        "Effect" : "Allow",
        "Action" : [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan",
          "dynamodb:Query",
        ],
        Resource = [
          "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.dynamodb_table_name}",
          "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.dynamodb_table_name}/*",
        ],
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logging_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_iam_role_policy_attachment" "lambda_dynamodb_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_dynamodb.arn
}

resource "aws_lambda_function" "lambda" {
  function_name = var.lambda_name
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.repo.repository_url}:${var.image_tag}"
  role          = aws_iam_role.lambda_exec_role.arn
  architectures = ["${var.architecture}"]
  memory_size   = var.memory_size
  timeout       = var.timeout
  environment {
    variables = [var.environment_variables, var.default_environment_variables]
  }
}

resource "aws_lambda_permission" "allow_sqs" {
  statement_id  = "AllowSQSTrigger"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.arn
  principal     = "sqs.amazonaws.com"
  source_arn    = var.sqs_arn
}

output "lambda_arn" {
  description = "The ARN of the deployed Lambda function"
  value       = aws_lambda_function.lambda.arn
}
