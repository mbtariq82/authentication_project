resource "aws_security_group" "postgres" {
  name        = "auth-postgres-sg"
  description = "Allow RDS access only from FastAPI"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "auth-postgres-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "postgres_from_fastapi" {
  security_group_id            = aws_security_group.postgres.id
  referenced_security_group_id = aws_security_group.fastapi.id
  description                  = "Allow PostgreSQL connections from FastAPI EC2"

  from_port   = 5432
  to_port     = 5432
  ip_protocol = "tcp"
}

