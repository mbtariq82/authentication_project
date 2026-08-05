variable "admin_cidr" {
  description = "Public IP address allowed to access the EC2 instance"
  type        = string
}

variable "db_username" {
  type      = string
  sensitive = true
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "fastapi_ami_id" {
  description = "Pinned AMI for the FastAPI EC2 instance"
  type        = string
  default     = "ami-054818ecdf7d5ec33"
}