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
            "ap_name" = "tna-external-services-backup",
            "ap_path" = "tna-external-services-backup",
            "actions" = [
                "s3:PutObject",
            ],
            "role_arns" = [
                "arn:aws:iam::637423167251:role/ec2-tna-service-backup-role"
            ]
        },
        {
            "ap_name" = "ds-live-digital-files-backup",
            "ap_path" = "ds-digital-files-backup",
            "actions" = [
                "s3:PutObject",
            ],
            "role_arns" = [
                "arn:aws:iam::846769538626:role/digital-files-backup"
            ]
        },
        {
            "ap_name" = "digital-services",
            "ap_path" = "digital-services",
            "actions" = [
                "s3:PutObject",
                "s3:AbortMultipartUpload",
            ],
            "role_arns" = [
                "arn:aws:iam::968803923593:role/lambda-s3-backup-monitor-role",
                "arn:aws:iam::846769538626:role/mysql-main-prime-role"
            ]
        },
    ]

    default_tags = local.default_tags
}

module "s3-bv-digital-services" {
    source = "./s3/bv-digital-services"

    tna_backup_inventory_arn = module.s3-tna-backup-inventory.tna_backup_inventory_arn
    default_tags             = local.default_tags
}

module "s3-bv-ds-digital-files" {
    source = "./s3/bv-ds-digital-files"

    tna_backup_inventory_arn = module.s3-tna-backup-inventory.tna_backup_inventory_arn
    default_tags             = local.default_tags
}

module "s3-bv-tna-external-services" {
    source = "./s3/bv-tna-external-services"

    tna_backup_inventory_arn = module.s3-tna-backup-inventory.tna_backup_inventory_arn
    default_tags             = local.default_tags
}


# ------------------------------------------------

module "s3-tna-backup-intake" {
    source = "./s3/tna-backup-intake"

    tna_backup_inventory_arn = module.s3-tna-backup-inventory.tna_backup_inventory_arn

    bkup_access_points = [
        {
            "ap_name" = "ds-backup-target",
            "ap_path" = "digital-services",
            "actions" = [
                "s3:PutObject",
            ],
            "role_arns" = [
                "arn:aws:iam::846769538626:role/mysql-main-prime-role",
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
