data "aws_caller_identity" "current" {}

data "aws_ssm_parameter" "vpc_info" {
    name = "/infrastructure/network/vpc"
}

data "aws_ssm_parameter" "public_subnet_a_info" {
    name = "/infrastructure/network/public-sub-a"
}

data "aws_ssm_parameter" "private_subnet_a_info" {
    name = "/infrastructure/network/private-sub-a"
}

data "aws_ssm_parameter" "mysql_main_prime_volume_id" {
    name = "/infrastructure/databases/mysql-main-prime/volume_id"
}

data "aws_ssm_parameter" "route53_private_zone_id" {
    name = "/infrastructure/route53/private-zone-id"
}
