module "iam" {
    source = "./iam"

    queue_arns = [
        module.sqs-backup-check-in.backup_check_in_queue_arn,
        module.sqs-backup-check-in.backup_check_in_dl_queue_arn,
        module.sqs-backup-check-in.backup_compressor_queue_arn,
        module.sqs-backup-check-in.backup_compressor_dl_queue_arn,
    ]
    default_tags = local.default_tags
}
