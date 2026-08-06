resource "aws_eks_cluster" "main" {
  name     = "authentication-project"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = var.eks_version

  access_config {
    authentication_mode                         = "API"
    bootstrap_cluster_creator_admin_permissions = false
  }

  vpc_config {
    subnet_ids = [
      aws_subnet.app_private_a.id,
      aws_subnet.app_private_b.id,
    ]

    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = [var.admin_cidr]
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster,
  ]
}

resource "aws_eks_node_group" "general" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "general"
  node_role_arn   = aws_iam_role.eks_nodes.arn

  subnet_ids = [
    aws_subnet.app_private_a.id,
    aws_subnet.app_private_b.id,
  ]

  instance_types = ["t3.small"]
  capacity_type  = "ON_DEMAND"
  disk_size      = 20

  scaling_config {
    min_size     = 2
    desired_size = 2
    max_size     = 4
  }

  update_config {
    max_unavailable = 1
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node,
    aws_iam_role_policy_attachment.eks_ecr_pull,
    aws_iam_role_policy_attachment.eks_cni,
  ]
}