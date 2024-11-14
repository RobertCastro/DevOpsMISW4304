resource "aws_security_group" "db_security_group" {
  name        = "database-security-group"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = aws_vpc.main.id

  # Allow outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "RDS Security Group"
  }
}

# Allow inbound PostgreSQL traffic from ECS tasks
resource "aws_security_group_rule" "postgres_from_ecs" {
  type                     = "ingress"
  from_port               = 5432
  to_port                 = 5432
  protocol                = "tcp"
  source_security_group_id = aws_security_group.lb_sg.id
  security_group_id       = aws_security_group.db_security_group.id
  description            = "Allow PostgreSQL access from ECS tasks"
}

# Create private subnets for RDS
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "Private Subnet ${count.index + 1}"
  }
}

# Create DB subnet group
resource "aws_db_subnet_group" "db_subnet_group" {
  name        = "database-subnet-group"
  description = "Database subnet group"
  subnet_ids  = aws_subnet.private[*].id
}

# Create RDS instance
resource "aws_db_instance" "postgres" {
  identifier           = "postgres-instance"
  engine              = "postgres"
  engine_version      = "14"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  max_allocated_storage = 100
  
  db_name             = "postgres"
  username           = "postgres"
  password           = "secret-database-password" # TODO: Use AWS Secrets Manager in production

  db_subnet_group_name   = aws_db_subnet_group.db_subnet_group.name
  vpc_security_group_ids = [aws_security_group.db_security_group.id]
  
  publicly_accessible    = false
  skip_final_snapshot    = true  # Set to false in production
  deletion_protection    = false  # Set to true in production

  tags = {
    Name = "PostgreSQL Database"
  }
}