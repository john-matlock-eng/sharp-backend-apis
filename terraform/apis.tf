
module "user_management_api" {
  source          = "./modules/api_deployment"
  aws_region      = var.aws_region
  api_name        = "user_management_api"
  lambda_handler  = "app.main.handler"
  runtime         = "python3.12"
  image_tag       = var.image_tag
  build_platform  = "linux/arm64"
}
