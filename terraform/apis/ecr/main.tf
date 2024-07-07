# ECR Repository
resource "aws_ecr_repository" "repo" {
  name                 = var.api_name
  image_tag_mutability = "IMMUTABLE"
  encryption_configuration {
    encryption_type = "AES256"
  }
  image_scanning_configuration {
    scan_on_push = true
  }
}
