resource "aws_db_instance" "postgres" {
  identifier = "auth-postgres"

  engine         = "postgres"
  instance_class = "db.t4g.micro"

  allocated_storage = 20
  storage_type      = "gp3"
  storage_encrypted = true

  db_name  = "authentication"
  username = var.db_username
  password = var.db_password
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.postgres.name
  vpc_security_group_ids = [aws_security_group.postgres.id]

  publicly_accessible = false
  multi_az            = false

  # Suitable for a disposable learning database.
  # Production should normally retain a final snapshot.
  skip_final_snapshot = true

  tags = {
    Name = "auth-postgres"
  }
}