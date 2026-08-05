resource "aws_instance" "fastapi" {
  ami           = var.fastapi_ami_id
  instance_type = "t3.micro"

  subnet_id              = aws_subnet.public_a.id
  vpc_security_group_ids = [aws_security_group.fastapi.id]
  key_name               = aws_key_pair.admin.key_name
  iam_instance_profile   = aws_iam_instance_profile.fastapi.name

  root_block_device {
    volume_size = 12
    encrypted   = true
  }
}