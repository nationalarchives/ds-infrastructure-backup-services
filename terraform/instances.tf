module "da-sftp-x-posts" {
    source = "./instances/da-sftp-x-posts"

    vpc_id = local.vpc_info.id

    image_id      = data.aws_ami.da_sftp_x_posts.id
    instance_type = "t3a.micro"
    key_name      = "da-x-post-backup-eu-west-2"
    subnet_id     = local.public_subnet_a_info.id
    volume_size   = 200

    default_tags = local.default_tags
}

module "service-backups" {
    source = "./instances/service-backups"

    vpc_id = local.vpc_info.id

    image_id      = data.aws_ami.service_backups.id
    instance_type = "t3a.micro"
    key_name      = "service-backups-eu-west-2"
    subnet_id     = local.private_subnet_a_info.id
    volume_size   = 20
    private_subnet_cidr_block = local.private_subnet_a_info.cidr_block

    default_tags = local.default_tags
}

module "shared-lb" {
    source = "./instances/shared-load-balancer"

    vpc_id = local.vpc_info.id
    subnet_id = local.public_subnet_a_info.id

    backup_drop_zone_instance_id = module.backup-drop-zone.backup_intake_instance_id
    cert_arn = "arn:aws:acm:eu-west-2:637423167251:certificate/e17f7cd3-4a44-4380-b06c-59d688355cea"

    tags = local.default_tags
}

module "backup-drop-zone" {
    source = "./instances/backup-drop-zone"

    image_id      = data.aws_ami.backup_drop_zone.id
    instance_type = "t3a.large"
    volume_size   = 100
    key_name      = "backup-drop-zone-eu-west-2"

    vpc_id    = local.vpc_info.id
    subnet_id = local.private_subnet_a_info.id


    tags = local.default_tags
}

module "mysql-main-prime" {
    source = "./instances/mysql-main-prime"

    resource_identifier = "main-prime"

    mysql_main_availability_zone = "eu-west-2a"

    account_id = data.aws_caller_identity.current.account_id
    secret_id = "/infrastructure/credentials/mysql-main*"

    # iam
    s3_deployment_bucket         = "tna-backup-tooling"
    s3_folder                    = "mysql"
    backup_bucket                = "tna-backup-intake"
    attach_ebs_volume_policy_arn = module.iam.attach_ebs_volume_policy_arn

    # instances
    ami_id        = data.aws_ami.mysql_main_ami.id
    instance_type = "t3a.large"
    volume_size   = 100
    key_name      = "mysql-main-ds-backup-eu-west-2"

    disable_api_termination = true
    monitoring              = true

    attached_ebs_volume_id = data.aws_ssm_parameter.mysql_main_prime_volume_id.value

    # network
    vpc_id          = local.vpc_info.id
    db_subnet_cidrs = [
        local.private_subnet_a_info.cidr_block,
    ]

    db_subnet_id = local.private_subnet_a_info.id
    public_subnet_cidr_block = local.public_subnet_a_info.cidr_block
    private_subnet_cidr_block = local.private_subnet_a_info.cidr_block

    zone_id   = data.aws_ssm_parameter.route53_private_zone_id.value
    mysql_dns = "mysql-main-prime.backup.local"

    tags = merge(local.default_tags, {
        Product = "MySQL"
    })
}
