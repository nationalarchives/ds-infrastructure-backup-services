resource "aws_security_group" "da_x_posts_backup" {
    name        = "da-x-posts-backup"
    description = "x posts backups security group"
    vpc_id      = var.vpc_id

    tags = merge(var.default_tags, {
        Name = "beta-rp"
    })
}

resource "aws_security_group_rule" "sftp_ingress" {
    cidr_blocks       = [
        "0.0.0.0/0"
    ]
    description       = "allow sftp access to instance"
    from_port         = 22
    to_port           = 22
    protocol          = "tcp"
    security_group_id = aws_security_group.da_x_posts_backup.id
    type              = "ingress"
}

resource "aws_security_group_rule" "rp_response_ingress" {
    cidr_blocks       = [
        "192.168.2.0/23"
    ]
    description       = "allow response from internal subnets"
    from_port         = 1024
    to_port           = 65535
    protocol          = "tcp"
    security_group_id = aws_security_group.da_x_posts_backup.id
    type              = "ingress"
}

resource "aws_security_group_rule" "rp_egress" {
    from_port         = 0
    to_port           = 0
    protocol          = "-1"
    security_group_id = aws_security_group.da_x_posts_backup.id
    type              = "egress"
    cidr_blocks       = [
        "0.0.0.0/0"
    ]
}
