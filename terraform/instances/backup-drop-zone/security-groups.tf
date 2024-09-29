##
# instance security group
#
resource "aws_security_group" "backup_drop_zone" {
    name        = "backup-drop-zone"
    description = "backup drop zone security group"
    vpc_id      = var.vpc_id

    tags = merge(var.tags, {
        Name = "backup-intake"
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

resource "aws_security_group_rule" "response_ingress" {
    cidr_blocks       = [
        "0.0.0.0/0",
    ]
    description       = "allow response coming in from anywhere"
    from_port         = 49152
    to_port           = 65535
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

resource "aws_security_group_rule" "ephemeral_egress" {
    cidr_blocks       = [
        "0.0.0.0/0",
    ]
    description = "allow instance respond to requests"
    from_port         = 49152
    to_port           = 65535
    protocol          = "tcp"
    security_group_id = aws_security_group.backup_drop_zone.id
    type              = "egress"
}
##
# load balancer security group
#
