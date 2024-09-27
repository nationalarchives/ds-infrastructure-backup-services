##
# shared load balancer
#
resource "aws_security_group" "shared_lb" {
    name        = "shared-lb"
    description = "HTTP and HTTPS access"
    vpc_id      = var.vpc_id

    tags = merge(var.tags, {
        Name = "shared-lb"
    })
}

resource "aws_security_group_rule" "shared_lb_http_ingress" {
    cidr_blocks = [
        "0.0.0.0/0",
    ]
    description       = "port 80 will be redirected to 443"
    from_port         = 80
    protocol          = "tcp"
    security_group_id = aws_security_group.shared_lb.id
    to_port           = 80
    type              = "ingress"
}

resource "aws_security_group_rule" "shared_lb_https_ingress" {
    cidr_blocks = [
        "0.0.0.0/0",
    ]
    description       = "443 traffic from anywhere"
    from_port         = 443
    protocol          = "tcp"
    security_group_id = aws_security_group.shared_lb.id
    to_port           = 443
    type              = "ingress"
}

resource "aws_security_group_rule" "shared_lb_http_egress" {
    cidr_blocks = [
        "0.0.0.0/0",
    ]
    security_group_id = aws_security_group.shared_lb.id
    type              = "egress"
    from_port         = 49152
    to_port           = 65535
    protocol          = "tcp"
}
