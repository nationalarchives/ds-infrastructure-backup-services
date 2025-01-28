#module "route53" {
#    source = "./route53"
#
#    public_domain = "tna-backup-drop-zone.nationalarchives.gov.uk"
#    load_balancer_dns_name = module.ec2-shared-lb.load_balancer_dns_name
#
#    tags = local.default_tags
#}
