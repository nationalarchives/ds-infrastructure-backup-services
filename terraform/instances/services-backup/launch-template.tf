resource "aws_launch_template" "services_backup" {
    name = "services-backup"

    iam_instance_profile {
        arn = aws_iam_instance_profile.ec2_tna_services_backup_profile.arn
    }

    image_id               = var.image_id
    instance_type          = "t3a.nano"
    key_name               = "service-backup-eu-west-2"
    update_default_version = true

    vpc_security_group_ids = var.security_group_ids

    user_data = base64encode(file("${path.module}/scripts/userdata.sh"))

    block_device_mappings {
        device_name = "/dev/xvda"

        ebs {
            volume_size = var.volume_size
            encrypted   = true
        }
    }

    metadata_options {
        http_endpoint               = "enabled"
        http_tokens                 = "required"
        http_put_response_hop_limit = 1
        instance_metadata_tags      = "enabled"
    }
}
