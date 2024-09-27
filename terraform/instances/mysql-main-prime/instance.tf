resource "aws_instance" "mysql_main" {
    launch_template {
        id      = aws_launch_template.mysql_main_prime.id
        version = "$$Latest"
    }
    subnet_id                   = var.db_subnet_id
    associate_public_ip_address = false

    root_block_device {
        tags = {
            Name = "mysql-${var.resource_identifier}-root"
        }
    }

    tags = merge(var.tags, {
        Name = "mysql-${var.resource_identifier}"
    })
}

resource "aws_volume_attachment" "ebs_attachment" {
    device_name = "/dev/xvdf"
    volume_id   = var.attached_ebs_volume_id
    instance_id = aws_instance.mysql_main.id

    skip_destroy = true
}
