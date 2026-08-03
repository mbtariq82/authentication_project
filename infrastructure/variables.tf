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