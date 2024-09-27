resource "aws_launch_template" "mysql_main_prime" {
    name = "mysql-main-prime"

    iam_instance_profile {
        arn = aws_iam_instance_profile.instance_profile.arn
    }

    image_id      = var.ami_id
    instance_type = var.instance_type
    key_name      = var.key_name

    update_default_version      = true
    disable_api_termination     = true

    vpc_security_group_ids = [
        aws_security_group.mysql_main.id,
    ]

    user_data = base64encode(file("${path.module}/scripts/userdata.sh"))

    block_device_mappings {
        device_name = "/dev/xvda"

        ebs {
            encrypted   = true
            volume_size = var.volume_size
            volume_type = "standard"
        }
    }

    metadata_options {
        http_endpoint               = "enabled"
        http_tokens                 = "required"
        http_put_response_hop_limit = 1
        instance_metadata_tags      = "enabled"
    }

    monitoring {
        enabled = true
    }
}
