resource "aws_s3_bucket" "artifact_store" {
  bucket = "python-app-pipeline-artifacts"
  force_destroy = true
  lifecycle {
    prevent_destroy = false  
  }
}

resource "aws_s3_bucket_versioning" "artifact_store_versioning" {
  bucket = aws_s3_bucket.artifact_store.id
  versioning_configuration {
    status = "Enabled"
  }
  
}
