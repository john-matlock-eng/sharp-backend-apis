# IAM Role for Lambda
# resource "aws_iam_role" "lambda_exec" {
#   name               = "${var.api_name}_api_lambda_exec"
#   assume_role_policy = <<EOF
#   {
#     "Version": "2012-10-17",
#     "Statement": [
#       {
#         "Action": "sts:AssumeRole",
#         "Principal": {
#           "Service": "lambda.amazonaws.com"
#         },
#         "Effect": "Allow",
#         "Sid": ""
#       }
#     ]
#   }
#   EOF
# }

data "aws_iam_role" "api_lambda_exec" {
  name = "api_lambda_exec"
}


resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = data.aws_iam_policy.api_lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
