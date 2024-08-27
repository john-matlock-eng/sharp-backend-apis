aws_region          = "us-east-2"
lambda_name         = "web_scraper"
dynamodb_table_name = "sharp_app_data"
architecture        = "x86_64"
memory_size         = 512
timeout             = 60
environment_variables = {
  LOG_LEVEL = "INFO"
}
