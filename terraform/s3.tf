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
        #        {
        #            "ap_name" = "github-backup",
        #            "ap_path" = "github-backup",
        #            "actions" = [
        #                "s3:PutObject",
        #            ]
        #            "role_arns" = [
        #                "arn:aws:iam::846769538626:role/digital-files-backup"
        #            ]
        #        },
        #        {
        #            "ap_name" = "tna-services-bkup-github",
        #            "ap_path" = "tna-services-bkup-github",
        #            "actions" = [
        #                "s3:PutObject",
        #            ]
        #            "role_arns" = [
        #                "arn:aws:iam::846769538626:role/digital-files-backup"
        #            ]
        #        },
        {
            "ap_name" = "tna-external-services-backup",
            "ap_path" = "tna-external-services-backup",
            "actions" = [
                "s3:PutObject",
            ]
            "role_arns" = [
                "arn:aws:iam::846769538626:role/digital-files-backup",
            ]
        },
        {
            "ap_name" = "ds-live-digital-files-backup",
            "ap_path" = "ds-digital-files-backup",
            "actions" = [
                "s3:PutObject",
            ]
            "role_arns" = [
                "arn:aws:iam::846769538626:role/digital-files-backup",
            ]
        },
        {
            "ap_name" = "ds-bkup-databases",
            "ap_path" = "digital-services/ds-bkup-databases",
            "actions" = [
                "s3:PutObject",
            ]
            "role_arns" = [
                "arn:aws:iam::846769538626:role/mysql-main-prime-role",
            ]
        },
        {
            "ap_name" = "digital-services",
            "ap_path" = "digital-services",
            "actions" = [
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:ListMultipartUploadParts",
                "s3:ListMultipartUploadParts",
                "s3:AbortMultipartUpload",
            ]
            "role_arns" = [
                "arn:aws:iam::968803923593:role/lambda-s3-backup-monitor-role",
                "arn:aws:iam::846769538626:role/mysql-main-prime-role",
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

module "s3-ds-live-digital-files-backup" {
    source = "./s3/ds-live-digital-files-backup"

    tna_backup_inventory_arn = module.s3-tna-backup-inventory.tna_backup_inventory_arn

    default_tags = local.default_tags
}

module "s3-tna-external-services-backup" {
    source = "./s3/tna-external-services-backup"

    tna_backup_inventory_arn = module.s3-tna-backup-inventory.tna_backup_inventory_arn
    default_tags             = local.default_tags
}

#import {
#  to = module.s3-ds-live-digital-files-backup.aws_s3_bucket.ds_live_digital_files_backup
#  id = "ds-live-digital-files-backup"
#}
#import {
#  to = module.s3-ds-live-digital-files-backup.aws_s3_bucket_ownership_controls.ds_live_digital_files_backup
#  id = "ds-live-digital-files-backup"
#}
#import {
#  to = module.s3-ds-live-digital-files-backup.aws_s3_bucket_server_side_encryption_configuration.ds_live_digital_files_backup
#  id = "ds-live-digital-files-backup"
#}
#import {
#  to = module.s3-ds-live-digital-files-backup.aws_s3_bucket_public_access_block.ds_live_digital_files_backup
#  id = "ds-live-digital-files-backupe"
#}
#import {
#  to = module.s3-ds-live-digital-files-backup.aws_s3_access_point.backup_access_point["ds-backup-target"]
#  id = "637423167251:ds-backup-target"
#}
#import {
#  to = module.s3-ds-live-digital-files-backup.aws_s3control_access_point_policy.ap_policy["ds-backup-target"]
#  id = "arn:aws:s3:eu-west-2:637423167251:accesspoint/ds-backup-target"
#}
#import {
#  to = module.s3-ds-live-digital-files-backup.aws_s3_bucket_policy.tna_backup_intake_access_from_another_account
#  id = "ds-live-digital-files-backup"
#}
