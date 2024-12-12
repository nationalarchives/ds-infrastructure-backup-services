module "network" {
    source = "./network"

    vpc_cidr = "192.168.0.0/22"

    public_cidr    = "192.168.0.0/23"
    public_az      = "eu-west-2a"
    public_name    = "public-eu-west-2a"
    private_cidr_a = "192.168.2.0/23"
    private_az_a   = "eu-west-2a"
    private_name_a = "private-eu-west-2a"

    default_tags = local.default_tags
}
