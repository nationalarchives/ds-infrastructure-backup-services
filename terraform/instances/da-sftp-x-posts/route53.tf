resource "aws_route53_zone" "sftp_public" {
    name = "da-sftp-xposts.nationalarchives.gov.uk"

    tags = {
        Service   = "da x posts backup"
        Terraform = true
    }
}

resource "aws_route53_record" "sftp_public" {
    zone_id = aws_route53_zone.sftp_public.zone_id
    name    = "da-sftp-xposts.nationalarchives.gov.uk"
    type    = "A"
    ttl     = 300
    records = [
        aws_instance.x_posts_backup.public_ip,
    ]
}
