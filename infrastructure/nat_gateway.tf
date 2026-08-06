resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name = "auth-nat-eip"
  }
}

resource "aws_nat_gateway" "app" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_a.id

  depends_on = [
    aws_internet_gateway.main,
  ]

  tags = {
    Name = "auth-app-nat"
  }
}