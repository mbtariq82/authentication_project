resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true # remove this when we move EC2 to the private subnet

  tags = {
    Name = "auth-public-a"
  }
}

resource "aws_subnet" "cache_private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = aws_subnet.public_a.availability_zone

  map_public_ip_on_launch = false

  tags = {
    Name = "auth-learning-cache-private-a"
  }
}