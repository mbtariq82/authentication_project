resource "aws_instance" "fastapi" {
  ami           = var.fastapi_ami_id
  instance_type = "t3.micro"

  subnet_id              = aws_subnet.public_a.id
  vpc_security_group_ids = [aws_security_group.fastapi.id]
  key_name               = aws_key_pair.admin.key_name
  iam_instance_profile   = aws_iam_instance_profile.fastapi.name

  user_data = <<-EOF
    #!/bin/bash
    set -euxo pipefail

    dnf install -y docker
    systemctl enable --now docker
    systemctl enable --now amazon-ssm-agent
    usermod -aG docker ec2-user
    install -d -m 700 /opt/authentication-project
  EOF

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
  }

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 12
    encrypted             = true
    delete_on_termination = true
  }

  tags = {
    Name = "authentication-project-fastapi"
  }
}

resource "aws_eip" "fastapi" {
  domain = "vpc"

  tags = {
    Name = "authentication-project-fastapi"
  }
}

resource "aws_eip_association" "fastapi" {
  allocation_id = aws_eip.fastapi.id
  instance_id   = aws_instance.fastapi.id

  depends_on = [
    aws_internet_gateway.main,
  ]
}
