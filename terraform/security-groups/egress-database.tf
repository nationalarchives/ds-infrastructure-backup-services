resource "aws_security_group" "ec2_egress_database" {
    name        = "ec2-egress-database"
    description = "egress over port 3306"
    vpc_id      = var.vpc_id

    tags = merge(var.tags, {
        Name = "ec2-egress-database"
    })
}

resource "aws_vpc_security_group_egress_rule" "database_egress" {
    count = length(var.db_subnet_cidrs)

    cidr_ipv4         = var.db_subnet_cidrs[count.index]
    from_port         = 3306
    ip_protocol       = "tcp"
    security_group_id = aws_security_group.ec2_egress_database.id
    to_port           = 3306

    tags = merge(var.tags, {
        Name = "ec2-egress-database[${count.index}]"
    })
}
