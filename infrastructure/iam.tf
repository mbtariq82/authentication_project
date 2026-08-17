resource "aws_iam_role" "fastapi_ec2" {
  name = "authentication-project-fastapi-ec2"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"

      Principal = {
        Service = "ec2.amazonaws.com"
      }

      Action = "sts:AssumeRole"
    }]
  })

  tags = {
    Name = "authentication-project-fastapi-ec2"
  }
}

resource "aws_iam_role_policy_attachment" "fastapi_ecr_pull" {
  role       = aws_iam_role.fastapi_ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly"
}

resource "aws_iam_role_policy_attachment" "fastapi_ssm" {
  role       = aws_iam_role.fastapi_ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

data "aws_iam_policy_document" "fastapi_telemetry" {
  statement {
    sid    = "ExportTracesToXRay"
    effect = "Allow"

    actions = [
      "xray:PutTelemetryRecords",
      "xray:PutTraceSegments",
    ]

    resources = ["*"]
  }

  statement {
    sid    = "DiscoverCloudWatchMetricLogs"
    effect = "Allow"

    actions = [
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
    ]

    resources = ["*"]
  }

  statement {
    sid    = "WriteCloudWatchMetricLogs"
    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      "${aws_cloudwatch_log_group.telemetry_metrics.arn}:*",
    ]
  }
}

resource "aws_iam_role_policy" "fastapi_telemetry" {
  name   = "authentication-project-telemetry"
  role   = aws_iam_role.fastapi_ec2.id
  policy = data.aws_iam_policy_document.fastapi_telemetry.json
}

resource "aws_iam_instance_profile" "fastapi" {
  name = "authentication-project-fastapi"
  role = aws_iam_role.fastapi_ec2.name
}
