# (FastAPI) Public Subnet
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "auth-internet-gateway"
  }
}
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "auth-public-route-table"
  }
}
resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}
resource "aws_route_table_association" "public_b" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "app_private" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "auth-app-private-route-table"
  }
}
resource "aws_route" "app_private_internet" {
  route_table_id         = aws_route_table.app_private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.app.id
}
resource "aws_route_table_association" "private_a" {
  subnet_id      = aws_subnet.app_private_a.id
  route_table_id = aws_route_table.app_private.id
}
resource "aws_route_table_association" "private_b" {
  subnet_id      = aws_subnet.app_private_b.id
  route_table_id = aws_route_table.app_private.id
}



# DB Private Subnet
resource "aws_route_table" "db_private" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "auth-db-private-route-table"
  }
}
resource "aws_route_table_association" "db_private_a" {
  subnet_id      = aws_subnet.db_private_a.id
  route_table_id = aws_route_table.db_private.id
}
resource "aws_route_table_association" "db_private_b" {
  subnet_id      = aws_subnet.db_private_b.id
  route_table_id = aws_route_table.db_private.id
}


# Cache Private Subnet
resource "aws_route_table" "cache_private" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "auth-cache-private-route-table"
  }
}
resource "aws_route_table_association" "cache_private_a" {
  subnet_id      = aws_subnet.cache_private_a.id
  route_table_id = aws_route_table.cache_private.id
}