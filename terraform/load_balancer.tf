
resource "aws_lb" "app_lb" {
  name               = "my-application-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb_sg.id]
  subnets            = aws_subnet.public[*].id  # Use the new public subnets

  enable_deletion_protection = false

  tags = {
    Environment = "production"
  }
}