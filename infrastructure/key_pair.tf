resource "aws_key_pair" "admin" {
  key_name   = "auth-learning-admin"
  public_key = file(pathexpand("~/.ssh/authentication_project.pub"))
}