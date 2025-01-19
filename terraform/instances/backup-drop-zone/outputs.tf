output "ec2_drop_zone_profile_arn" {
    value = aws_iam_instance_profile.ec2_drop_zone_profile.arn
}

output "drop_zone_instance_id" {
    value = aws_instance.backup_drop_zone.id
}
