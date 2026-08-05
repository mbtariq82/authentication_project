output "fastapi_public_ip" {
  description = "Public IP address of the FastAPI EC2 instance"
  value       = aws_instance.fastapi.public_ip
}

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

output "alb_dns_name" {
  description = "Public DNS name of the Application Load Balancer"
  value       = aws_lb.fastapi.dns_name
}

output "fastapi_url" {
  description = "FastAPI URL through the Application Load Balancer"
  value       = "http://${aws_lb.fastapi.dns_name}"
}

output "fastapi_target_group_arn" {
  description = "ARN of the FastAPI target group"
  value       = aws_lb_target_group.fastapi.arn
}