resource "aws_cognito_user_pool" "user_pool" {
  name = "my_user_pool"

  auto_verified_attributes = ["email"]

  schema {
    name                = "username"
    required            = true
    mutable             = false
    attribute_data_type = "String"
  }

  schema {
    name                = "email"
    required            = true
    mutable             = true
    attribute_data_type = "String"
  }

  schema {
    name                = "custom:moniker"
    attribute_data_type = "String"
    mutable             = true
    required            = true
  }

  admin_create_user_config {
    allow_admin_create_user_only = false
  }

  password_policy {
    minimum_length    = 14
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  lambda_config {
    post_confirmation = aws_lambda_function.cognito_post_confirmation.arn
  }
}

resource "aws_cognito_user_pool_client" "user_pool_client" {
  user_pool_id                 = aws_cognito_user_pool.user_pool.id
  name                         = "sharp_user_pool_client"
  generate_secret              = false
  explicit_auth_flows          = ["ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"]
  supported_identity_providers = ["COGNITO"]
}

resource "aws_cognito_user_pool_domain" "user_pool_domain" {
  domain       = "sharp-meng"
  user_pool_id = aws_cognito_user_pool.user_pool.id
}

resource "aws_lambda_function" "cognito_post_confirmation" {
  function_name = "cognito_post_confirmation"
  package_type  = "Image"
  image_uri     = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/user_management:${var.image_tag}"
  role          = aws_iam_role.user_signup_lambda_cognito_role.arn
  memory_size   = 256
  timeout       = 60

  environment {
    variables = {
      TABLE_NAME = var.dynamodb_table_name
    }
  }
}

output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.user_pool.id
}