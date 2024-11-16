resource "aws_ecr_repository" "python_app" {
  name                 = "python_app"
  image_tag_mutability = "MUTABLE"
  force_delete = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "Python App Repository"
  }

  lifecycle {
    prevent_destroy = false  # Allow the resource to be destroyed
  }
}

# Grant pull and push permissions to CodeBuild
resource "aws_ecr_repository_policy" "codebuild_policy" {
  repository = aws_ecr_repository.python_app.name
  policy     = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "CodeBuildAccess"
        Effect = "Allow"
        Principal = {
          Service = "codebuild.amazonaws.com"
        }
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
      }
    ]
  })
}

# Grant pull permissions to ECS tasks
resource "aws_ecr_repository_policy" "ecs_policy" {
  repository = aws_ecr_repository.python_app.name
  policy     = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ECSAccess"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability"
        ]
      }
    ]
  })
}

output "repository_uri" {
  value       = aws_ecr_repository.python_app.repository_url
  description = "The URI of the ECR repository"
}