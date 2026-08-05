resource "aws_security_group" "fastapi" {
  name        = "auth-fastapi-sg"
  description = "Security group for the FastAPI EC2 instance"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "auth-fastapi-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "fastapi_ssh" {
  security_group_id = aws_security_group.fastapi.id
  description       = "Allow SSH from administrator IP"

  cidr_ipv4   = var.admin_cidr
  from_port   = 22
  to_port     = 22
  ip_protocol = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "fastapi_api" {
  security_group_id            = aws_security_group.fastapi.id
  referenced_security_group_id = aws_security_group.alb.id
  description                  = "Allow FastAPI traffic from the ALB"

  from_port   = 8000
  to_port     = 8000
  ip_protocol = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "fastapi_outbound" {
  security_group_id = aws_security_group.fastapi.id
  description       = "Allow all outbound IPv4 traffic"

  cidr_ipv4   = "0.0.0.0/0"
  ip_protocol = "-1"
}