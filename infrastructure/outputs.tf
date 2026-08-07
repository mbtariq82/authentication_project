output "frontend_website_url" {
  description = "HTTP URL of the public React S3 website"
  value       = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}"
}

output "valkey_endpoint" {
  value = aws_elasticache_replication_group.valkey.primary_endpoint_address
}

output "postgres_endpoint" {
  description = "PostgreSQL RDS endpoint including port"
  value       = aws_db_instance.postgres.endpoint
}
output "postgres_database_name" {
  description = "Initial PostgreSQL database name"
  value       = aws_db_instance.postgres.db_name
}

output "fastapi_ecr_repository_url" {
  value = aws_ecr_repository.fastapi.repository_url
}

output "github_actions_deploy_role_arn" {
  description = "IAM role ARN used by GitHub Actions through OIDC"
  value       = aws_iam_role.github_actions_deploy.arn
}

