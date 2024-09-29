# -----------------------------------------------------------------------------
# External shared Load Balancer
# -----------------------------------------------------------------------------
resource "aws_lb" "shared_lb" {
    name               = "shared-lb"
    internal           = false
    load_balancer_type = "application"

    security_groups = [
        aws_security_group.shared_lb.id
    ]

    subnets = [
        var.subnet_id,
    ]

    tags = var.tags
}

resource "aws_lb_target_group" "backup_intake" {
    name     = "backup-intake"
    port     = 80
    protocol = "HTTP"
    vpc_id   = var.vpc_id

    health_check {
        interval            = 30
        path                = "/get/status"
        port                = "traffic-port"
        timeout             = 5
        healthy_threshold   = 2
        unhealthy_threshold = 2
        matcher             = "200"
    }

    tags = var.tags
}

resource "aws_lb_target_group_attachment" "backup_intake" {
    target_group_arn = aws_lb_target_group.backup_intake.arn
    target_id        = var.backup_drop_zone_instance_id
    port             = 80
}

resource "aws_lb_listener" "http" {
    default_action {
        type = "redirect"
        redirect {
            port        = "443"
            protocol    = "HTTPS"
            status_code = "HTTP_301"
        }
    }
    protocol          = "HTTP"
    load_balancer_arn = aws_lb.shared_lb.arn
    port              = 80
}

resource "aws_lb_listener" "https" {
    default_action {
        type             = "forward"
        target_group_arn = aws_lb_target_group.backup_intake.arn
    }
    protocol          = "HTTPS"
    load_balancer_arn = aws_lb.shared_lb.arn
    port              = 443
}

resource "aws_lb_listener_rule" "host_based_weighted_routing" {
    listener_arn = aws_lb_listener.https.arn
    priority     = 99

    action {
        type             = "forward"
        target_group_arn = aws_lb_target_group.backup_intake.arn
    }

    condition {
        host_header {
            values = [
                "backup-intake.nationalarchives.gov.uk",
            ]
        }
    }
}

resource "aws_lb_listener_certificate" "wc-cert" {
    listener_arn    = aws_lb_listener.https.arn
    certificate_arn = var.cert_arn
}
