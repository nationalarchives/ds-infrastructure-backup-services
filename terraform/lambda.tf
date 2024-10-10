#variable "notifications_channel" {}

#module "slack-notifications" {
#    source                = "./lambda/slack_notifications"
#    notifications_channel = var.notifications_channel
#}

module "backup-check-in" {
    source = "./lambda/backup-check-in"

    region         = "eu-west-2"
    aws_account_id = data.aws_caller_identity.current.account_id

    bucket_arn  = module.s3-tna-backup-drop-zone.tna_backup_drop_zone_arn
    bucket_name = module.s3-tna-backup-drop-zone.tna_backup_drop_zone_name

    vpc_id = local.vpc_info.id
    subnet_ids = [
        local.private_subnet_a_info.id,
    ]
    private_subnet_cidr = local.private_subnet_a_info.cidr_block

    security_group_ids = []

    runtime = "python3.12"
    layers = [
        data.klayers_package_latest_version.boto3-3_12.arn,
        data.klayers_package_latest_version.mysql-connector-python-3_12.arn,
        aws_lambda_layer_version.datetime_5_5.arn,
    ]

    tags = local.default_tags
}
