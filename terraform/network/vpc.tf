resource "aws_vpc" "base_vpc" {
    cidr_block           = var.vpc_cidr
    enable_dns_hostnames = true

    tags = merge(var.default_tags, {
        Name = "base-vpc"
    })
}

resource "aws_security_group" "sts_security_group" {
    name        = "base-vpc-sts-endpoint"
    description = "access to sts vpc endpoint from vpc"
    vpc_id      = aws_vpc.base_vpc.id

    tags = merge(var.default_tags, {
        Name = "base-vpc-sts-endpoint"
    })
}

resource "aws_security_group_rule" "sts_security_group_433" {
    type              = "ingress"
    from_port         = 443
    to_port           = 443
    protocol          = "tcp"
    security_group_id = aws_security_group.sts_security_group.id
    description       = "access from vpc"
    cidr_blocks = [
        var.private_cidr_a,
    ]
}


resource "aws_vpc_endpoint" "sts" {
    vpc_id            = aws_vpc.base_vpc.id
    service_name      = "com.amazonaws.eu-west-2.sts"
    vpc_endpoint_type = "Interface"

    security_group_ids = [
        aws_security_group.sts_security_group.id
    ]
    subnet_ids = [
        aws_subnet.public_sub.id,
    ]
    private_dns_enabled = false

    tags = merge(var.default_tags, {
        Name = "base-vpc"
    })
}
