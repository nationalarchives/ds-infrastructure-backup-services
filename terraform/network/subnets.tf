resource "aws_subnet" "public_sub" {
    vpc_id            = aws_vpc.base_vpc.id
    cidr_block        = var.public_cidr
    availability_zone = var.public_az

    map_public_ip_on_launch = true

    tags = merge(var.default_tags, {
        Name = var.public_name
    })
}

resource "aws_subnet" "private_sub_a" {
    vpc_id            = aws_vpc.base_vpc.id
    cidr_block        = var.private_cidr_a
    availability_zone = var.private_az_a

    map_public_ip_on_launch = false

    tags = merge(var.default_tags, {
        Name = var.private_name_a
    })
}
