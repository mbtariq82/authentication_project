resource "aws_iam_openid_connect_provider" "github_actions" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com",
  ]

  tags = {
    Name = "authentication-project-github-actions"
  }
}

data "aws_iam_policy_document" "github_actions_assume_role" {
  statement {
    sid    = "AllowGitHubActionsForMainBranch"
    effect = "Allow"

    principals {
      type = "Federated"
      identifiers = [
        aws_iam_openid_connect_provider.github_actions.arn,
      ]
    }

    actions = [
      "sts:AssumeRoleWithWebIdentity",
    ]

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values = [
        "repo:mbtariq82@119065609/authentication_project@1304042998:ref:refs/heads/main",
      ]
    }
  }
}

resource "aws_iam_role" "github_actions_deploy" {
  name               = "authentication-project-github-deploy"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role.json

  tags = {
    Name = "authentication-project-github-deploy"
  }
}

data "aws_iam_policy_document" "github_actions_deploy" {
  statement {
    sid    = "GetEcrAuthorizationToken"
    effect = "Allow"

    actions = [
      "ecr:GetAuthorizationToken",
    ]

    resources = ["*"]
  }

  statement {
    sid    = "PushFastapiImages"
    effect = "Allow"

    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:CompleteLayerUpload",
      "ecr:GetDownloadUrlForLayer",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
    ]

    resources = [
      aws_ecr_repository.fastapi.arn,
    ]
  }

  statement {
    sid    = "DescribeEksCluster"
    effect = "Allow"

    actions = [
      "eks:DescribeCluster",
    ]

    resources = [
      aws_eks_cluster.main.arn,
    ]
  }
}

resource "aws_iam_role_policy" "github_actions_deploy" {
  name   = "authentication-project-github-deploy"
  role   = aws_iam_role.github_actions_deploy.id
  policy = data.aws_iam_policy_document.github_actions_deploy.json
}

resource "aws_eks_access_entry" "github_actions_deploy" {
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = aws_iam_role.github_actions_deploy.arn
  type          = "STANDARD"
}

resource "aws_eks_access_policy_association" "github_actions_deploy" {
  cluster_name  = aws_eks_cluster.main.name
  principal_arn = aws_iam_role.github_actions_deploy.arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSEditPolicy"

  access_scope {
    type       = "namespace"
    namespaces = ["auth-development"]
  }

  depends_on = [
    aws_eks_access_entry.github_actions_deploy,
  ]
}
