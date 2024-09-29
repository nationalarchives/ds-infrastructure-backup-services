resource "aws_iam_policy" "ec2_tna_backup_drop_zone_policy" {
    name        = "tna-backup-drop-zone-policy"
    description = "allowing to process intake of backups between s3 buckets for ec2"

    policy = file("${path.module}/templates/ec2-tna-backup-drop-zone-policy.json")
}
