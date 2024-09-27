resource "aws_route53_record" "instance" {
    zone_id = var.zone_id
    name    = var.mysql_dns
    type    = "CNAME"
    ttl     = 5
    records = [
        aws_instance.mysql_main.private_dns,
    ]
}
