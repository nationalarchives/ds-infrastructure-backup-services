resource "aws_iam_policy" "ec2_da_x_posts_backup_policy" {
    name        = "da-x-posts-backup-policy"
    description = "access to da_x_posts s3 for ec2"

    policy = file("${path.module}/templates/ec2-da-x-posts-backup-policy.json")
}
