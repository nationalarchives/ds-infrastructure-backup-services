resource "aws_iam_policy" "ec2_tna_service_backup_policy" {
    name        = "tna_service_backup_policy"
    description = "access to tna_service_backup s3 for ec2"

    policy = file("${path.module}/templates/ec2-tna-service-backup-policy.json")
}
