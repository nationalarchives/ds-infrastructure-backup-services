resource "aws_route_table" "public" {
    vpc_id = aws_vpc.base_vpc.id

    tags = merge(var.default_tags, {
        Name = "base-vpc-public"
    })
}

resource "aws_route" "public_route_internet" {
    route_table_id = aws_route_table.public.id
    gateway_id     = aws_internet_gateway.base_vpc_internet_gateway.id

    destination_cidr_block = "0.0.0.0/0"
}

resource "aws_route_table_association" "public_rt_assoc" {
    subnet_id      = aws_subnet.public_sub.id
    route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
    vpc_id = aws_vpc.base_vpc.id

    tags = merge(var.default_tags, {
        Name = "base-vpc-private"
    })
}

resource "aws_route" "private_internet_a" {
    route_table_id = aws_route_table.private.id
    nat_gateway_id = aws_nat_gateway.nat_gateway.id

    destination_cidr_block = "0.0.0.0/0"
}

resource "aws_route_table_association" "private_rt_assoc_a" {
    subnet_id      = aws_subnet.private_sub_a.id
    route_table_id = aws_route_table.private.id
}
