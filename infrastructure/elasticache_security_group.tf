resource "aws_security_group" "valkey" {
  name        = "auth-learning-valkey-sg"
  description = "Allow Valkey access only from FastAPI"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "auth-learning-valkey-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "valkey_from_fastapi" {
  security_group_id            = aws_security_group.valkey.id
  referenced_security_group_id = aws_security_group.fastapi.id
  description                  = "Allow Valkey connections from FastAPI EC2"

  from_port   = 6379
  to_port     = 6379
  ip_protocol = "tcp"
}

