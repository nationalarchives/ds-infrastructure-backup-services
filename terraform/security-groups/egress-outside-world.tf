resource "aws_security_group" "outside_world" {
    name        = "ec2-egress-outside-world"
    description = "egress over port 80 and 443"
    vpc_id      = var.vpc_id

    tags = merge(var.tags, {
        Name = "ec2-egress-outside-world"
    })
}

resource "aws_vpc_security_group_egress_rule" "http_egress" {
    cidr_ipv4         = "0.0.0.0/0"
    from_port         = 80
    ip_protocol       = "tcp"
    security_group_id = aws_security_group.outside_world.id
    to_port           = 80

    tags = merge(var.tags, {
        Name = "ec2-egress-http"
    })
}

resource "aws_vpc_security_group_egress_rule" "https_egress" {
    cidr_ipv4         = "0.0.0.0/0"
    from_port         = 443
    ip_protocol       = "tcp"
    security_group_id = aws_security_group.outside_world.id
    to_port           = 443

    tags = merge(var.tags, {
        Name = "ec2-egress-https"
    })
}
