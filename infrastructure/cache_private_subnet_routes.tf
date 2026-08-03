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