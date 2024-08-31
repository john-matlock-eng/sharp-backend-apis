provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

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

resource "aws_iam_policy" "lambda_logging" {
  name        = "${var.api_name}_lambda_logging_policy"
  description = "IAM policy for logging from a lambda"

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
  name        = "${var.api_name}_lambda_dynamodb_policy"
  description = "IAM policy for logging from a lambda"

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
          "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/sharp_app_data",
          "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/sharp_app_data/*",
        ],
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_dynamodb_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_dynamodb.arn
}

resource "aws_iam_role_policy_attachment" "lambda_logging_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_lambda_function" "lambda" {
  function_name = var.api_name
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.api_ecr_repository.repository_url}:${var.image_tag}"
  role          = aws_iam_role.lambda_exec_role.arn
  architectures = ["x86_64"]
  memory_size   = var.memory_size
  timeout       = var.timeout
  environment {
    variables = {
      USER_POOL_ID                                 = var.cognito_user_pool_id,
      APP_CLIENT_ID                                = var.cognito_user_pool_client_id
      COGNITO_REGION                               = var.aws_region
      KNOWLEDGE_SOURCE_URL_INITIAL_INGESTION_QUEUE = var.knowledge_source_url_initial_ingestion_queue
    }
  }
}


resource "aws_iam_policy" "api_lambda_sqs_policy" {
  name        = "${var.api_name}_api_lambda_sqs_policy"
  description = "Policy for Lambda to send messages to SQS"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "sqs:SendMessage"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "api_lambda_policy_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.api_lambda_sqs_policy.arn
}
