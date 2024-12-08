resource "aws_iam_role" "ec2_backup_drop_zone" {
    assume_role_policy = file("${path.root}/templates/assume-role-ec2-policy.json")
    name = "ec2-backup-drop-zone-role"
    description = "allow ec2 access to tna-backup-drop-zone"
    tags = var.default_tags
}

resource "aws_iam_role_policy_attachment" "ec2_drop_zone_policy" {
    role       = aws_iam_role.ec2_backup_drop_zone.id
    policy_arn = aws_iam_policy.ec2_drop_zone_policy.arn
}

resource "aws_iam_role_policy_attachment" "AmazonEC2RoleforSSM" {
    role       = aws_iam_role.ec2_backup_drop_zone.id
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM"
}

resource "aws_iam_role_policy_attachment" "SecretsManagerReadWrite" {
    role       = aws_iam_role.ec2_backup_drop_zone.id
    policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
}

resource "aws_iam_instance_profile" "ec2_backup_drop_zone" {
    name = "ec2-backup-drop-zone-role"
    role = aws_iam_role.ec2_backup_drop_zone.name
}
