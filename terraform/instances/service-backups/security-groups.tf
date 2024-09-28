resource "aws_security_group" "service_backups" {
    name        = "service-backups"
    description = "service backups security group"
    vpc_id      = var.vpc_id

    tags = merge(var.default_tags, {
        Name = "beta-rp"
    })
}

resource "aws_vpc_security_group_ingress_rule" "rp_response_ingress" {
    cidr_blocks = [
        var.private_subnet_cidr_block,
    ]
    description       = "allow response from internal subnets"
    from_port         = 1024
    to_port           = 65535
    ip_protocol       = "tcp"
    security_group_id = aws_security_group.service_backups.id
}

resource "aws_vpc_security_group_egress_rule" "rp_egress" {
    cidr_blocks = [
        "0.0.0.0/0"
    ]
    from_port         = 0
    to_port           = 0
    ip_protocol       = "-1"
    security_group_id = aws_security_group.service_backups.id
}
