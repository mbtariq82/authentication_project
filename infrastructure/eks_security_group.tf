resource "aws_vpc_security_group_ingress_rule" "postgres_from_eks" {
  security_group_id            = aws_security_group.postgres.id
  referenced_security_group_id = aws_eks_cluster.main.vpc_config[0].cluster_security_group_id
  description                  = "Allow PostgreSQL connections from EKS"

  from_port   = 5432
  to_port     = 5432
  ip_protocol = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "valkey_from_eks" {
  security_group_id            = aws_security_group.valkey.id
  referenced_security_group_id = aws_eks_cluster.main.vpc_config[0].cluster_security_group_id
  description                  = "Allow Valkey connections from EKS"

  from_port   = 6379
  to_port     = 6379
  ip_protocol = "tcp"
}