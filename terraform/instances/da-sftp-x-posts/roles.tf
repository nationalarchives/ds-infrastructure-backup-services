resource "aws_iam_role" "ec2_da_x_posts_backup_role" {
    name = "ec2-da-x-posts-role"
    assume_role_policy = file("${path.module}/templates/ec2_assume_role.json")
}

resource "aws_iam_instance_profile" "ec2_da_x_posts_backup_profile" {
    name = "ec2-da-x-posts-profile"
    path = "/"
    role = aws_iam_role.ec2_da_x_posts_backup_role.name
}

resource "aws_iam_role_policy_attachment" "backup" {
    role       = aws_iam_role.ec2_da_x_posts_backup_role.name
    policy_arn = aws_iam_policy.ec2_da_x_posts_backup_policy.arn
}

resource "aws_iam_role_policy_attachment" "ssm" {
    role       = aws_iam_role.ec2_da_x_posts_backup_role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM"
}

resource "aws_iam_role_policy_attachment" "asm" {
    role       = aws_iam_role.ec2_da_x_posts_backup_role.name
    policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
}

