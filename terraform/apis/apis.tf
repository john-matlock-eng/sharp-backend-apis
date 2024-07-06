
module "api_deployment" {
  source          = "./modules/api_deployment"
  aws_region      = var.aws_region
  api_name        = var.api_name
  lambda_handler  = "app.main.handler"
  runtime         = "python3.12"
  image_tag       = var.image_tag
  build_platform  = "linux/arm64"
}
