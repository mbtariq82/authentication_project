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
    sid    = "DeployFastapiThroughSsm"
    effect = "Allow"

    actions = [
      "ssm:SendCommand",
    ]

    resources = [
      aws_instance.fastapi.arn,
      "arn:aws:ssm:eu-west-2::document/AWS-RunShellScript",
    ]
  }

  statement {
    sid    = "ReadFastapiDeploymentResult"
    effect = "Allow"

    actions = [
      "ssm:GetCommandInvocation",
    ]

    resources = ["*"]
  }

  statement {
    sid    = "ListFrontendBucket"
    effect = "Allow"

    actions = [
      "s3:ListBucket",
    ]

    resources = [
      aws_s3_bucket.frontend.arn,
    ]
  }

  statement {
    sid    = "DeployFrontendToS3"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
    ]

    resources = [
      "${aws_s3_bucket.frontend.arn}/*",
    ]
  }
}

resource "aws_iam_role_policy" "github_actions_deploy" {
  name   = "authentication-project-github-deploy"
  role   = aws_iam_role.github_actions_deploy.id
  policy = data.aws_iam_policy_document.github_actions_deploy.json
}
