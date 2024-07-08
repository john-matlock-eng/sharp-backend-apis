provider "aws" {
  region = var.aws_region
}

data "aws_ecr_repository" "api_ecr_repository" {
  name = "${var.api_name}"
}

resource "aws_lambda_function" "lambda" {
  function_name = var.api_name
  image_uri     = "${data.aws_ecr_repository.api_ecr_repository.repository_url}:${var.image_tag}"
  handler       = var.lambda_handler
  runtime       = var.runtime
  role          = aws_iam_role.lambda_exec.arn
}

# # API Gateway
# resource "aws_api_gateway_rest_api" "api" {
#   name = var.api_name
# }

# resource "aws_api_gateway_resource" "resource" {
#   rest_api_id = aws_api_gateway_rest_api.api.id
#   parent_id   = aws_api_gateway_rest_api.api.root_resource_id
#   path_part   = "users"
# }

# resource "aws_api_gateway_method" "method" {
#   rest_api_id   = aws_api_gateway_rest_api.api.id
#   resource_id   = aws_api_gateway_resource.resource.id
#   http_method   = "GET"
#   authorization = "NONE"
# }

# resource "aws_api_gateway_integration" "integration" {
#   rest_api_id             = aws_api_gateway_rest_api.api.id
#   resource_id             = aws_api_gateway_resource.resource.id
#   http_method             = aws_api_gateway_method.method.http_method
#   integration_http_method = "POST"
#   type                    = "AWS_PROXY"
#   uri                     = aws_lambda_function.lambda.invoke_arn
# }

# output "api_gateway_url" {
#   value = aws_api_gateway_rest_api.api.execution_arn
# }
