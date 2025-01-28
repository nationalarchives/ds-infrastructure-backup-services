output "sg_outside_world_arn" {
    value = aws_security_group.outside_world.arn
}

output "sg_outside_world_id" {
    value = aws_security_group.outside_world.id
}

output "sg_database_arn" {
    value = aws_security_group.ec2_egress_database.arn
}

output "sg_database_id" {
    value = aws_security_group.ec2_egress_database.id
}
