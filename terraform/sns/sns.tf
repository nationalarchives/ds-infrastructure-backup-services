variable "account_id" {}
variable "bucket_arn" {}
variable "topic" {}

resource "aws_sns_topic" "s3_backup_check_in_topic" {
    name = "s3-backup-check-in-topic"
    policy = templatefile(templatefile("${path.module}/templates/sns-publish-policy.json", {
        account_id = var.account_id,
        bucket_arn = var.bucket_arn,
        topic = var.topic
    }))
}

output "s3_backup_check_in_topic_arn" {
    value = aws_sns_topic.s3_backup_check_in_topic.arn
}
