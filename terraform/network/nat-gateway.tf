resource "aws_eip" "nat_gateway" {
    domain = "vpc"

    tags = merge(var.default_tags, {
        Name        = "base-vpc-nat-gateway-eip"
        Description = "eip for nat gateway"
    })
}

resource "aws_nat_gateway" "nat_gateway" {
    allocation_id = aws_eip.nat_gateway.id
    subnet_id     = aws_subnet.public_sub.id

    tags = merge(var.default_tags, {
        Name = "base-vpc-nat-gateway"
    })
}
