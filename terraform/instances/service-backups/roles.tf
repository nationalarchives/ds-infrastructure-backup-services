resource "aws_iam_role" "ec2_tna_service_backup_role" {
    name = "ec2-tna-service-backup-role"
    assume_role_policy = file("${path.module}/templates/ec2_assume_role.json")

    managed_policy_arns = [
        aws_iam_policy.ec2_tna_service_backup_policy.arn,
        "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM",
        "arn:aws:iam::aws:policy/SecretsManagerReadWrite",
    ]
}

resource "aws_iam_instance_profile" "ec2_tna_service_backup_profile" {
    name = "ec2-tna-service-backup-profile"
    path = "/"
    role = aws_iam_role.ec2_tna_service_backup_role.name
}
