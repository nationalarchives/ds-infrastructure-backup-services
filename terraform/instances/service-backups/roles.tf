resource "aws_iam_role" "ec2_tna_service_backup_role" {
    name = "ec2-tna-service-backup-role"
    assume_role_policy = file("${path.module}/templates/ec2_assume_role.json")
}

resource "aws_iam_instance_profile" "ec2_tna_service_backup_profile" {
    name = "ec2-tna-service-backup-profile"
    path = "/"
    role = aws_iam_role.ec2_tna_service_backup_role.name
}

resource "aws_iam_role_policy_attachment" "ec2_ssm" {
    role       = aws_iam_role.ec2_tna_service_backup_role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM"
}

resource "aws_iam_role_policy_attachment" "asm" {
    role       = aws_iam_role.ec2_tna_service_backup_role.name
    policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
}

resource "aws_iam_role_policy_attachment" "ec2_backup" {
    role       = aws_iam_role.ec2_tna_service_backup_role.name
    policy_arn = aws_iam_policy.ec2_tna_service_backup_policy.arn
}

