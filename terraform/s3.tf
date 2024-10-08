module "s3-ds-backup-kpf-administration" {
    source = "./s3/ds-backup-kpf-administration"

    default_tags = local.default_tags
}

module "s3-da-sftp-intake" {
    source = "./s3/da-sftp-intake"

    default_tags = local.default_tags
}

module "s3-tna-backup-drop-zone" {
    source = "./s3/tna-backup-drop-zone"

    tna_backup_inventory_arn = module.s3-tna-backup-inventory.tna_backup_inventory_arn

    bkup_drop_zone_access_points = [
        {
            "ap_name" = "ds-bkup-databases",
            "ap_path" = "digital-services/databases",
            "role_arns" = [
                "arn:aws:iam::846769538626:role/mysql-main-prime-role"
            ]
        },
    ]

    default_tags = local.default_tags
}

module "s3-tna-backup-intake" {
    source = "./s3/tna-backup-intake"

    tna_backup_inventory_arn = module.s3-tna-backup-inventory.tna_backup_inventory_arn

    bkup_access_points = [
        {
            "ap_name" = "ds-backup-target",
            "ap_path" = "digital-services",
            "role_arns" = [
                "arn:aws:iam::846769538626:role/mysql-main-prime-role"
            ]
        },
    ]

    default_tags = local.default_tags
}

module "s3-tna-backup-inventory" {
    source = "./s3/tna-backup-inventory"

    default_tags = local.default_tags
}

module "s3-tna-backup-tooling" {
    source = "./s3/tna-backup-tooling"

    default_tags = local.default_tags
}

module "s3-tna-backup-vault" {
    source = "./s3/tna-backup-vault"

    tna_backup_inventory_arn = module.s3-tna-backup-inventory.tna_backup_inventory_arn

    default_tags = local.default_tags
}

module "s3-tna-service-backup" {
    source = "./s3/tna-service-backup"

    tna_backup_inventory_arn = module.s3-tna-backup-inventory.tna_backup_inventory_arn

    default_tags = local.default_tags
}

#import {
#  to = module.s3-tna-backup-intake.aws_s3_bucket.tna_backup_intake
#  id = "tna-backup-intake"
#}
#import {
#  to = module.s3-tna-backup-intake.aws_s3_bucket_ownership_controls.tna_backup_intake
#  id = "tna-backup-intake"
#}
#import {
#  to = module.s3-tna-backup-intake.aws_s3_bucket_server_side_encryption_configuration.tna_backup_intake
#  id = "tna-backup-intake"
#}
#import {
#  to = module.s3-tna-backup-intake.aws_s3_bucket_public_access_block.tna_backup_intake
#  id = "tna-backup-intake"
#}
#import {
#  to = module.s3-tna-backup-intake.aws_s3_access_point.backup_access_point["ds-backup-target"]
#  id = "637423167251:ds-backup-target"
#}
#import {
#  to = module.s3-tna-backup-intake.aws_s3control_access_point_policy.ap_policy["ds-backup-target"]
#  id = "arn:aws:s3:eu-west-2:637423167251:accesspoint/ds-backup-target"
#}
#import {
#  to = module.s3-tna-backup-intake.aws_s3_bucket_policy.tna_backup_intake_access_from_another_account
#  id = "tna-backup-intake"
#}
