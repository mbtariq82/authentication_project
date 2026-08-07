resource "aws_security_group" "valkey" {
  name        = "auth-learning-valkey-sg"
  description = "Allow Valkey access only from FastAPI"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "auth-learning-valkey-sg"
  }
}

