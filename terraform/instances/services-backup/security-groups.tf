#resource "aws_security_group" "services_backup" {
#    name        = "services-backup"
#    description = "services backup security group"
#    vpc_id      = var.vpc_id
#
#    tags = merge(var.default_tags, {
#        Name = "service-backups"
#    })
#}
#
#resource "aws_vpc_security_group_ingress_rule" "response_ingress" {
#    cidr_ipv4         = var.private_subnet_cidr_block
#    description       = "allow response from internal subnets"
#    from_port         = 1024
#    to_port           = 65535
#    ip_protocol       = "tcp"
#    security_group_id = aws_security_group.service_backups.id
#}
#
#resource "aws_vpc_security_group_egress_rule" "all_egress" {
#    cidr_ipv4         = "0.0.0.0/0"
#    from_port         = -1
#    to_port           = -1
#    ip_protocol       = "-1"
#    security_group_id = aws_security_group.service_backups.id
#}
