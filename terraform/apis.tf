module "api_deployment" {
  source = "./modules/api_deployment"

  folder_path    = "./lambda_folder"
  api_name       = "user_management"
  lambda_handler = "lambda.handler"
  runtime        = "python3.12"
  build_platform = "linux/arm64"
#   image_tag      = var.image_tag
}
