module "s3" {
    source = "../../ds-infrastructure-backup-services/terraform/s3"

    bkup_access_points = [
        {
            "ap_name" = "ds-backup-target",
            "ap_path" = "digital-services",
            "role_arns" = [
                "arn:aws:iam::846769538626:role/mysql-main-prime-role"
            ]
        },
    ]

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
