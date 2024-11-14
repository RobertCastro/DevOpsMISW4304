resource "aws_codebuild_project" "docker_build_project" {
  name          = "docker-build-project"
  description   = "Builds and pushes Docker image to ECR"
  build_timeout = "30"
  service_role  = aws_iam_role.codebuild_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/standard:6.0"
    type                       = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode            = true

    environment_variable {
      name  = "ECR_REPOSITORY_URI"
      value = aws_ecr_repository.python_app.repository_url
    }

    environment_variable {
      name  = "AWS_REGION"
      value = data.aws_region.current.name
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = <<-EOT
version: 0.2
phases:
  pre_build:
    commands:
      - aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPOSITORY_URI
  build:
    commands:
      - pip install -r requirements.txt
      - export FLASK_ENV=testing
      - set -e
      - pytest tests/
      - docker build -t python_app:latest .
      - docker tag python_app:latest $ECR_REPOSITORY_URI:latest
  post_build:
    commands:
      - docker push $ECR_REPOSITORY_URI:latest
      - echo 'Image has been pushed to ECR'
EOT
  }
}