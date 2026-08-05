resource "aws_lb" "fastapi" {
  name               = "auth-fastapi-alb"
  internal           = false
  load_balancer_type = "application"

  security_groups = [
    aws_security_group.alb.id
  ]

  subnets = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id,
  ]

  enable_deletion_protection = false

  tags = {
    Name = "auth-fastapi-alb"
  }
}


resource "aws_lb_target_group" "fastapi" {
  name        = "auth-fastapi-targets"
  port        = 8000
  protocol    = "HTTP"
  target_type = "instance"
  vpc_id      = aws_vpc.main.id

  health_check {
    enabled             = true
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = {
    Name = "auth-fastapi-targets"
  }
}


resource "aws_lb_target_group_attachment" "fastapi" {
  target_group_arn = aws_lb_target_group.fastapi.arn
  target_id        = aws_instance.fastapi.id
  port             = 8000
}


resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.fastapi.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fastapi.arn
  }
}