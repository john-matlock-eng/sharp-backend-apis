resource "aws_iam_role" "api_lambda_exec" {
  name               = "${var.api_name}_api_lambda_exec"
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

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.api_lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
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
  role       = aws_iam_role.api_lambda_exec.name
  policy_arn = aws_iam_policy.api_lambda_sqs_policy.arn
}
