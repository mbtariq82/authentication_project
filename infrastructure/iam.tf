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

resource "aws_iam_instance_profile" "fastapi" {
  name = "authentication-project-fastapi"
  role = aws_iam_role.fastapi_ec2.name
}

data "aws_iam_policy_document" "fastapi_profile_images" {
  statement {
    sid    = "ManageProfileImages"
    effect = "Allow"

    actions = [
      "s3:DeleteObject",
      "s3:GetObject",
      "s3:PutObject",
    ]

    resources = [
      "${aws_s3_bucket.profile_images.arn}/profile-images/*",
    ]
  }
}

resource "aws_iam_role_policy" "fastapi_profile_images" {
  name   = "authentication-project-profile-images"
  role   = aws_iam_role.fastapi_ec2.id
  policy = data.aws_iam_policy_document.fastapi_profile_images.json
}
