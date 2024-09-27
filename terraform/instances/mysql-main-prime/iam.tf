resource "aws_iam_policy" "deployment_source_access_policy" {
    name        = "mysql-${var.resource_identifier}-deployment-source-access-policy"
    description = "access to deployment source"

    policy = templatefile("${path.root}/templates/s3-deployment-access-policy.json",
        {
            s3_deployment_bucket = var.s3_deployment_bucket
            folder               = var.s3_folder
        }
    )
}

resource "aws_iam_policy" "backup_policy" {
    name        = "mysql-${var.resource_identifier}-backup-policy"
    description = "permissions for backups"

    policy = templatefile("${path.root}/templates/database-backup-policy.json",
        {
            s3_bucket = var.backup_bucket
            secret_id = var.secret_id
            account_id = var.account_id
        }
    )
}

resource "aws_iam_role" "instance_role" {
    name               = "mysql-${var.resource_identifier}-role"
    assume_role_policy = file("${path.root}/templates/assume-role-ec2-policy.json")

    managed_policy_arns = [
        "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
        "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
        aws_iam_policy.deployment_source_access_policy.arn,
        aws_iam_policy.backup_policy.arn,
        var.attach_ebs_volume_policy_arn
    ]

    tags = var.tags
}

resource "aws_iam_instance_profile" "instance_profile" {
    name = "mysql-${var.resource_identifier}-profile"
    role = aws_iam_role.instance_role.name

    tags = var.tags
}
