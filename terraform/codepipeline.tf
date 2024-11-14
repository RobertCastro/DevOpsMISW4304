resource "aws_codepipeline" "ecr_pipeline" {
  name     = "python-app-ecr-pipeline"
  role_arn = aws_iam_role.codepipeline_role.arn

  artifact_store {
    location = aws_s3_bucket.artifact_store.bucket
    type     = "S3"
  }

  stage {
    name = "Source"

    action {
      name             = "GitHub_Source"
      category         = "Source"
      owner            = "ThirdParty"
      provider         = "GitHub"
      version          = "1"
      output_artifacts = ["source_output"]

      configuration = {
        Owner                = "DaGamez"
        Repo                 = "202415-devops-grupo9-compumundohipermegared"
        Branch              = "main"
        OAuthToken          = data.aws_secretsmanager_secret_version.github_token.secret_string
      }
    }
  }

  stage {
    name = "Build"

    action {
      name            = "Docker_Build_and_Push"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["source_output"]
      version         = "1"

      configuration = {
        ProjectName = aws_codebuild_project.docker_build_project.name
      }
    }
  }
}