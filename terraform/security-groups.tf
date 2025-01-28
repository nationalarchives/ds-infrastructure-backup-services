module "sgs" {
    source = "./security-groups"

    vpc_id = local.vpc_info.id
    db_subnet_cidrs = [
        local.private_subnet_a_info.cidr
    ]

    tags = local.default_tags
}
