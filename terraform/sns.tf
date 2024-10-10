module "backup-check-in" {
    source = "./sns"

    account_id = data.aws_caller_identity.current.account_id
    bucket_arn = module.s3-tna-backup-drop-zone.tna_backup_drop_zone_arn
    topic = "s3-backup-check-in-topic"
}
