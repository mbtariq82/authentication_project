data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-kernel-*-x86_64"]
  }
}

resource "aws_instance" "fastapi" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"

  subnet_id              = aws_subnet.public_a.id
  vpc_security_group_ids = [aws_security_group.fastapi.id]
  key_name               = aws_key_pair.admin.key_name

  root_block_device {
    volume_size = 12
    encrypted   = true
  }
}