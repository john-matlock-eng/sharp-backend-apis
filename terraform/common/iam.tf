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

resource "aws_iam_role" "user_signup_lambda_cognito_role" {
  name = "user_signup_lambda_cognito_role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [{
      "Action" : "sts:AssumeRole",
      "Effect" : "Allow",
      "Principal" : {
        "Service" : "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "user_signup_lambda_cognito_policy" {
  name = "user_signup_lambda_cognito_policy"
  role = aws_iam_role.user_signup_lambda_cognito_role.id
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ],
        "Resource" : "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.dynamodb_table_name}",
        "Condition" : {
          "ForAllValues:StringEquals" : {
            "dynamodb:LeadingKeys" : "USER#"
          },
          "ForAllValues:StringEqualsIfExists" : {
            "dynamodb:Attributes" : ["PK", "SK", "DataType", "Moniker", "CreatedAt"]
          }
        }
      }
    ]
  })
}