
module "api_deployment" {
  source                                       = "./modules/api_deployment"
  aws_region                                   = var.aws_region
  api_name                                     = var.api_name
  lambda_handler                               = "app.main.handler"
  runtime                                      = "python3.12"
  image_tag                                    = var.image_tag
  build_platform                               = "linux/arm64"
  memory_size                                  = 256
  timeout                                      = 30
  cognito_user_pool_id                         = var.cognito_user_pool_id
  cognito_user_pool_client_id                  = var.cognito_user_pool_client_id
  knowledge_source_url_initial_ingestion_queue = var.knowledge_source_url_initial_ingestion_queue
}
