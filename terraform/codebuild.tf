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
      - printf '{"executionRoleArn":"arn:aws:iam::061039766984:role/ecs-execution-role","family":"python-app-task","requiresCompatibilities":["FARGATE"],"networkMode":"awsvpc","cpu":"1024","memory":"3072","containerDefinitions":[{"name":"Container-app-python","image":"%s","essential":true,"portMappings":[{"containerPort":5000,"hostPort":5000,"protocol":"tcp"}],"logConfiguration":{"logDriver":"awslogs","options":{"awslogs-group":"/ecs/ContainerAppPythonLogs","awslogs-region":"us-west-2","awslogs-stream-prefix":"ContainerAppPythonLogs"}}}],"taskRoleArn":"arn:aws:iam::061039766984:role/ecs-task-role"}' $ECR_REPOSITORY_URI:latest > taskdef.json
      - printf '{"version":1,"Resources":[{"TargetService":{"Type":"AWS::ECS::Service","Properties":{"TaskDefinition":"<TASK_DEFINITION>","LoadBalancerInfo":{"ContainerName":"Container-app-python","ContainerPort":5000}}}}]}' > appspec.yaml
      - printf '[{"name":"Container-app-python","imageUri":"%s"}]' $ECR_REPOSITORY_URI:latest > imagedefinitions.json
      - echo 'Image has been pushed to ECR'
artifacts:
  files:
    - taskdef.json
    - appspec.yaml
    - imagedefinitions.json
EOT
  }
}