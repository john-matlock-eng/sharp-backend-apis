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

resource "aws_ecr_lifecycle_policy" "lifecycle_policy" {
  repository = aws_ecr_repository.repo.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 3 images"
        selection    = {
          tagStatus    = "any"
          countType    = "imageCountMoreThan"
          countNumber  = 3
        }
        action       = {
          type = "expire"
        }
      }
    ]
  })
}
