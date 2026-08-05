resource "aws_security_group" "alb" {
  name        = "auth-alb-sg"
  description = "Security group for the ALB"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "auth-alb-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "alb" {
  security_group_id = aws_security_group.alb.id
  description       = "Allow all inbound IPv4 traffic"

  cidr_ipv4   = "0.0.0.0/0"
  from_port   = 80
  to_port     = 80
  ip_protocol = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "alb_to_fastapi" {
  security_group_id            = aws_security_group.alb.id
  referenced_security_group_id = aws_security_group.fastapi.id
  description                  = "Allow ALB to reach FastAPI"

  from_port   = 8000
  to_port     = 8000
  ip_protocol = "tcp"
}
