resource "aws_iam_role" "ec2_tna_backup_drop_zone_role" {
    name = "ec2-tna-backup-intake-role"
    assume_role_policy = file("${path.module}/templates/ec2_assume_role.json")
}

resource "aws_iam_instance_profile" "ec2_tna_backup_drop_zone_profile" {
    name = "ec2-tna-backup-intake-profile"
    path = "/"
    role = aws_iam_role.ec2_tna_backup_drop_zone_role.name
}

resource "aws_iam_role_policy_attachment" "ec2_bucket_intake" {
    role       = aws_iam_role.ec2_tna_backup_drop_zone_role.name
    policy_arn = aws_iam_policy.ec2_tna_backup_drop_zone_policy.arn
}

resource "aws_iam_role_policy_attachment" "ec2_ssm" {
    role       = aws_iam_role.ec2_tna_backup_drop_zone_role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM"
}

resource "aws_iam_role_policy_attachment" "ec2_asm" {
    role       = aws_iam_role.ec2_tna_backup_drop_zone_role.name
    policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
}
