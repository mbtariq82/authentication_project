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