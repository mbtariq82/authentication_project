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

output "fastapi_ec2_instance_id" {
  description = "EC2 instance ID targeted by GitHub Actions through Systems Manager"
  value       = aws_instance.fastapi.id
}

output "fastapi_elastic_ip" {
  description = "Stable public IPv4 address for the FastAPI EC2 instance"
  value       = aws_eip.fastapi.public_ip
}

output "fastapi_url" {
  description = "Public FastAPI URL"
  value       = "http://${aws_eip.fastapi.public_ip}:8000"
}

output "github_actions_deploy_role_arn" {
  description = "IAM role ARN used by GitHub Actions through OIDC"
  value       = aws_iam_role.github_actions_deploy.arn
}

