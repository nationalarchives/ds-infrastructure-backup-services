resource "aws_security_group" "da_x_posts_backup" {
    name        = "da-x-posts-backup"
    description = "x posts backups security group"
    vpc_id      = var.vpc_id

    tags = merge(var.default_tags, {
        Name = "beta-rp"
    })
}

resource "aws_vpc_security_group_ingress_rule" "sftp_ingress" {
    cidr_ipv4         = "0.0.0.0/0"
    description       = "allow sftp access to instance"
    from_port         = 22
    to_port           = 22
    ip_protocol       = "tcp"
    security_group_id = aws_security_group.da_x_posts_backup.id
}

resource "aws_vpc_security_group_ingress_rule" "response_ingress" {
    cidr_ipv4         = "192.168.2.0/23"
    description       = "allow response from internal subnets"
    from_port         = 1024
    to_port           = 65535
    ip_protocol       = "tcp"
    security_group_id = aws_security_group.da_x_posts_backup.id
}

resource "aws_vpc_security_group_egress_rule" "egress" {
    from_port         = -1
    to_port           = -1
    ip_protocol       = "-1"
    security_group_id = aws_security_group.da_x_posts_backup.id
    cidr_ipv4         = "0.0.0.0/0"
}
