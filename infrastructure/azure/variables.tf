variable "location" {
  type    = string
  default = "uksouth"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "admin_ip" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}
