resource "aws_iam_policy" "lambda_policy" {
  name        = "lambda_policy"
  description = "IAM policy for Lambda to access DynamoDB"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
        ],
        Effect = "Allow",
        Resource = [
          "${aws_dynamodb_table.sharp_app_data.arn}",
          "${aws_dynamodb_table.sharp_app_data.arn}/*",
        ],
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource" : "*"
      },
    ],
  })
}

data "aws_iam_role" "api_lambda_exec" {
  name = "api_lambda_exec"
}

resource "aws_iam_policy_attachment" "api_lambda_policy_attachment" {
  name       = "api_lambda_policy_attachment"
  roles      = [data.aws_iam_role.api_lambda_exec.name]
  policy_arn = aws_iam_policy.lambda_policy.arn
}
