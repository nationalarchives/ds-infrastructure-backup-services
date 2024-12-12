resource "aws_internet_gateway" "base_vpc_internet_gateway" {
    vpc_id = aws_vpc.base_vpc.id

    tags = merge(var.default_tags, {
        Name = "base-vpc-internet-gateway"
    })
}
