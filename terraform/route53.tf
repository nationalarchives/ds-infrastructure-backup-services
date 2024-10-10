module "route53" {
    source = "./route53"

    public_domain = "tna-backup-intake.nationalarchives.gov.uk"
    load_balancer_dns_name = module.shared-lb.load_balancer_dns_name

    tags = local.default_tags
}
