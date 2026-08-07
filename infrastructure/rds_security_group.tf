resource "aws_security_group" "postgres" {
  name        = "auth-postgres-sg"
  description = "Allow RDS access only from FastAPI"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "auth-postgres-sg"
  }
}

