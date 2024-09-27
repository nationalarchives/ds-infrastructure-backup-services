output "mysql_main_prime_role_arn" {
    value = aws_iam_role.instance_role.arn
}

output "mysql_main_prime_role_name" {
    value = aws_iam_role.instance_role.name
}

output "mysql_main_prime_instance_profile_name" {
    value = aws_iam_instance_profile.instance_profile.name
}
