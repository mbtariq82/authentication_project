output "fastapi_public_ip" {
  description = "Public IP address of the FastAPI EC2 instance"
  value       = aws_instance.fastapi.public_ip
}