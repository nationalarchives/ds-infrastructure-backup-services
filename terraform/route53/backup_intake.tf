resource "aws_route53_zone" "tna_backup_intake" {
    name  = var.public_domain

    tags = var.tags
}

resource "aws_route53_record" "tna_backup_intake" {
    zone_id = aws_route53_zone.tna_backup_intake.zone_id
    name    = var.public_domain
    type    = "A"

    alias {
        name                   = var.load_balancer_dns_name
        zone_id                = aws_route53_zone.tna_backup_intake.zone_id
        evaluate_target_health = false
    }
}
