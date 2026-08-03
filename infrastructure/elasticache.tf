resource "aws_elasticache_subnet_group" "valkey" {
  name        = "auth-learning-valkey-subnets"
  description = "Private subnets for the authentication project Valkey cache"

  subnet_ids = [
    aws_subnet.cache_private_a.id,
  ]

  tags = {
    Name = "auth-learning-valkey-subnets"
  }
}


resource "aws_elasticache_replication_group" "valkey" {
  replication_group_id = "auth-learning-valkey"
  description          = "Valkey cache for the authentication project"

  engine         = "valkey"
  engine_version = "8.0"
  node_type      = "cache.t4g.micro"
  port           = 6379

  # One primary node with no replicas.
  num_cache_clusters         = 1
  automatic_failover_enabled = false
  multi_az_enabled           = false

  preferred_cache_cluster_azs = [
    aws_subnet.cache_private_a.availability_zone,
  ]

  subnet_group_name  = aws_elasticache_subnet_group.valkey.name
  security_group_ids = [aws_security_group.valkey.id]

  at_rest_encryption_enabled = true

  # FastAPI must connect using rediss:// when this is enabled.
  transit_encryption_enabled = true
  transit_encryption_mode    = "required"

  auto_minor_version_upgrade = true
  apply_immediately          = true

  tags = {
    Name = "auth-learning-valkey"
  }
}