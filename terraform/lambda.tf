module "lambda-backup-check-in" {
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

    queue_arn = module.sqs-backup-check-in.backup_check_in_queue_arn
    ssm_id    = "/application/backup/secure-backups"

    runtime   = "python3.12"
    layers = [
        data.klayers_package_latest_version.boto3-3_12.arn,
        data.klayers_package_latest_version.mysql-connector-python-3_12.arn,
        aws_lambda_layer_version.datetime_5_5.arn,
    ]

    bucket_id = module.s3-tna-backup-drop-zone.tna_backup_drop_zone_id
    topic_arn = module.sns-backup-check-in.s3_backup_check_in_topic_arn

    tags = local.default_tags
}
