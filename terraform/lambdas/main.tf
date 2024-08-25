module "lambda_deployment" {
  source                = "./modules/lambda_deployment"
  aws_region            = var.aws_region
  lambda_name           = var.lambda_name
  image_tag             = var.image_tag
  dynamodb_table_name   = var.dynamodb_table_name
  architecture          = var.architecture
  memory_size           = var.memory_size
  timeout               = var.timeout
  environment_variables = var.environment_variables
  sqs_arn               = var.sqs_arn
}
