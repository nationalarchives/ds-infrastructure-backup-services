resource "aws_security_group" "lambda_backup_drop_zone_sg" {
    name        = "lambda-test-drop-zone-sg"
    description = "lambda function for backup check-in"
    vpc_id      = var.vpc_id

    tags = merge(var.tags, {
        Name = "lambda-test-drop-zone-sg"
    })
}

resource "aws_vpc_security_group_ingress_rule" "replies" {
    security_group_id = aws_security_group.lambda_backup_drop_zone_sg.id

    cidr_ipv4   = "192.168.2.0/23"
    description = "traffic back from db"
    from_port   = 49152
    ip_protocol = "tcp"
    to_port     = 65535
}

resource "aws_vpc_security_group_egress_rule" "https" {
    security_group_id = aws_security_group.lambda_backup_drop_zone_sg.id

    cidr_ipv4   = "0.0.0.0/0"
    description = "https calls to the world"
    from_port   = 443
    ip_protocol = "tcp"
    to_port     = 443
}

resource "aws_vpc_security_group_egress_rule" "connect_mysql" {
    security_group_id = aws_security_group.lambda_backup_drop_zone_sg.id

    cidr_ipv4   = var.private_subnet_cidr
    description = "mysql connection"
    from_port   = 3306
    ip_protocol = "tcp"
    to_port     = 3306
}

resource "aws_vpc_security_group_egress_rule" "replies" {
    security_group_id = aws_security_group.lambda_backup_drop_zone_sg.id

    cidr_ipv4   = "0.0.0.0/0"
    description = "let in replies from outside"
    from_port   = 49152
    ip_protocol = "tcp"
    to_port     = 65535
}
