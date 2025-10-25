# Configure the AWS Provider
provider "aws" {
  region = "eu-central-1"
}

# Define the VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "my-vpc"
  }
}

# Define Subnets (at least two for Load Balancer availability)
resource "aws_subnet" "public_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.public_subnet_a_cidr
  availability_zone = "${var.region}a"
  map_public_ip_on_launch = true # Instances in this subnet will get a public IP

  tags = {
    Name = "public-subnet-a"
  }
}

resource "aws_subnet" "public_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.public_subnet_b_cidr
  availability_zone = "${var.region}b"
  map_public_ip_on_launch = true # Instances in this subnet will get a public IP

  tags = {
    Name = "public-subnet-b"
  }
}

# Create an Internet Gateway
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "internet-gateway"
  }
}

# Create a Route Table for Public Subnets
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "public-route-table"
  }
}

# Associate Public Subnets with the Public Route Table
resource "aws_route_table_association" "public_a_assoc" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "public_b_assoc" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public_rt.id
}

# Create an SSH Key Pair
resource "aws_key_pair" "deployer" {
  key_name   = "deployer-key"
  public_key = file(var.public_key_path)
}

# Create a Security Group for the EC2 Instance
resource "aws_security_group" "instance_sg" {
  name_prefix = "instance-sg-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Be cautious with this in production; restrict to known IPs
    description = "Allow SSH access"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "instance-security-group"
  }
}

# Create a Security Group for the Load Balancer
resource "aws_security_group" "lb_sg" {
  name_prefix = "lb-sg-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Adjust as needed for your application's port
    description = "Allow HTTP access"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Adjust as needed for HTTPS
    description = "Allow HTTPS access"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "load-balancer-security-group"
  }
}

# Create an EC2 Instance
resource "aws_instance" "app_server" {
  ami           = var.ami_id
  instance_type = "t2.micro"
  key_name      = aws_key_pair.deployer.key_name
  vpc_security_group_ids = [aws_security_group.instance_sg.id]
  subnet_id     = aws_subnet.public_a.id

  tags = {
    Name = "app-server"
  }
}

# Create a Target Group for the Load Balancer
resource "aws_lb_target_group" "app_tg" {
  port     = 80  # Application port
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path     = "/" # Adjust health check path as needed
    protocol = "HTTP"
    matcher  = "200"
    interval = 30
    timeout  = 5
  }
}

# Attach the EC2 Instance to the Target Group
resource "aws_lb_target_group_attachment" "app_tg_attach" {
  target_group_arn = aws_lb_target_group.app_tg.arn
  target_id        = aws_instance.app_server.id
  port             = 80 # Application port
}

# Create an Application Load Balancer
resource "aws_lb" "app_lb" {
  name_prefix    = "lb-"
  internal       = false
  load_balancer_type = "application"
  security_groups = [aws_security_group.lb_sg.id]
  subnets         = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id,
  ]

  enable_deletion_protection = false # Consider setting this to true in production
}

# Create a Listener for the Load Balancer (HTTP on Port 80)
resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.app_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}

# Output the Public IP of the Load Balancer
output "load_balancer_dns_name" {
  value = aws_lb.app_lb.dns_name
  description = "The DNS name of the application load balancer"
}

# Output the Public IP of the EC2 Instance (for direct SSH access)
output "instance_public_ip" {
  value = aws_instance.app_server.public_ip
  description = "The public IP address of the EC2 instance"
}

# Output the SSH private key (sensitive - handle with care!)
# output "ssh_private_key" {
#   value     = tls_private_key.deployer.private_key_pem
#   sensitive = true
#   description = "The private key for SSH access (handle with care!)"
# }
