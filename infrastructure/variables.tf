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
  description = "Pinned Amazon Linux 2023 AMI for the FastAPI EC2 instance"
  type        = string
  default     = "ami-054818ecdf7d5ec33"
}

variable "eks_admin_principal_arn" {
  description = "Permanent IAM or SSO role granted EKS administrator access"
  type        = string
}

variable "eks_version" {
  description = "Kubernetes version used by the EKS cluster"
  type        = string
  default     = "1.35"
}
