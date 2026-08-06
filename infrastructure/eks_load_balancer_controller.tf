data "aws_iam_policy_document" "load_balancer_controller_assume_role" {
  statement {
    sid    = "AllowEksAuthToAssumeRoleForPodIdentity"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["pods.eks.amazonaws.com"]
    }

    actions = [
      "sts:AssumeRole",
      "sts:TagSession",
    ]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestTag/kubernetes-namespace"
      values   = ["kube-system"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:RequestTag/kubernetes-service-account"
      values   = ["aws-load-balancer-controller"]
    }
  }
}

resource "aws_iam_role" "load_balancer_controller" {
  name               = "authentication-project-aws-load-balancer-controller"
  assume_role_policy = data.aws_iam_policy_document.load_balancer_controller_assume_role.json

  tags = {
    Name = "authentication-project-aws-load-balancer-controller"
  }
}

resource "aws_iam_policy" "load_balancer_controller" {
  name        = "authentication-project-aws-load-balancer-controller"
  description = "Permissions for AWS Load Balancer Controller v2.14.1"
  policy      = file("${path.module}/aws_load_balancer_controller_policy.json")
}

resource "aws_iam_role_policy_attachment" "load_balancer_controller" {
  role       = aws_iam_role.load_balancer_controller.name
  policy_arn = aws_iam_policy.load_balancer_controller.arn
}

resource "aws_eks_addon" "pod_identity_agent" {
  cluster_name = aws_eks_cluster.main.name
  addon_name   = "eks-pod-identity-agent"
}

resource "aws_eks_pod_identity_association" "load_balancer_controller" {
  cluster_name    = aws_eks_cluster.main.name
  namespace       = "kube-system"
  service_account = "aws-load-balancer-controller"
  role_arn        = aws_iam_role.load_balancer_controller.arn

  depends_on = [
    aws_eks_addon.pod_identity_agent,
    aws_iam_role_policy_attachment.load_balancer_controller,
  ]
}
