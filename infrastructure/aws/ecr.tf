resource "aws_ecr_repository" "fastapi" {
  name                 = "auth-fastapi"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "authentication-project-fastapi"
  }
}