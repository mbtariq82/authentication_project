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
}

resource "aws_iam_role_policy_attachment" "fastapi_ecr_pull" {
  role       = aws_iam_role.fastapi_ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly"
}

resource "aws_iam_instance_profile" "fastapi" {
  name = "authentication-project-fastapi"
  role = aws_iam_role.fastapi_ec2.name
}