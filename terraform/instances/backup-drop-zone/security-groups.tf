##
# instance security group
#
resource "aws_security_group" "backup_drop_zone_db" {
    name        = "backup-drop-zone"
    description = "backup drop zone security group"
    vpc_id      = var.vpc_id

    tags = merge(var.tags, {
        Name = "backup-drop-zone"
    })
}

resource "aws_vpc_security_group_ingress_rule" "self_ingress" {
    security_group_id = aws_security_group.backup_drop_zone.id

    referenced_security_group_id = aws_security_group.backup_drop_zone.id
    from_port                    = 1024
    ip_protocol                  = "tcp"
    to_port                      = 65535

    tags = merge(var.tags, {
        Name = "securitygroup-members"
    })
}

resource "aws_vpc_security_group_ingress_rule" "http_ingress" {
    count = length(var.subnet_cidrs)

    security_group_id = aws_security_group.backup_drop_zone.id

    cidr_ipv4   = var.subnet_cidrs[count.index]
    from_port   = 80
    ip_protocol = "tcp"
    to_port     = 80
    tags = merge(var.tags, {
        Name = "access-subnet"
    })
}

resource "aws_security_group_rule" "api_html_ingress" {
    cidr_blocks       = [
        "192.168.0.0/23",
        "192.168.2.0/23",
    ]
    description       = "allow HTTP from public and private subnet"
    from_port         = 80
    to_port           = 80
    protocol          = "tcp"
    security_group_id = aws_security_group.backup_drop_zone.id
    type              = "ingress"
}

resource "aws_security_group_rule" "api_htmls_ingress" {
    cidr_blocks       = [
        "192.168.0.0/23",
        "192.168.2.0/23",
    ]
    description       = "allow HTTPS from public and private subnet"
    from_port         = 443
    to_port           = 443
    protocol          = "tcp"
    security_group_id = aws_security_group.backup_drop_zone.id
    type              = "ingress"
}

resource "aws_security_group_rule" "http_egress" {
    cidr_blocks       = [
        "0.0.0.0/0",
    ]
    description = "allow instance requests over HTTP"
    from_port         = 80
    to_port           = 80
    protocol          = "tcp"
    security_group_id = aws_security_group.backup_drop_zone.id
    type              = "egress"
}

resource "aws_security_group_rule" "https_egress" {
    cidr_blocks       = [
        "0.0.0.0/0",
    ]
    description = "allow instance requests over HTTPS"
    from_port         = 443
    to_port           = 443
    protocol          = "tcp"
    security_group_id = aws_security_group.backup_drop_zone.id
    type              = "egress"
}
##
# load balancer security group
#
