resource "aws_instance" "services_backup" {
    ami                    = var.image_id
    instance_type          = var.instance_type
    key_name               = var.key_name
    iam_instance_profile   = aws_iam_instance_profile.ec2_tna_service_backup_profile.name
    vpc_security_group_ids = var.security_group_ids
    subnet_id              = var.subnet_id

    user_data = file("${path.module}/scripts/userdata.sh")

    metadata_options {
        http_tokens            = "required"
        instance_metadata_tags = "enabled"
        http_endpoint          = "enabled"
    }

    root_block_device {
        volume_size = var.volume_size
    }

    tags = merge(var.tags, {
        Name          = "services-backup"
        Service       = "backup"
        AutoSwitchOff = "false"
        AutoSwitchOn  = "false"
        CostCentre    = "TNA"
    })
}
