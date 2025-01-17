variable "default_tags" {}
variable "bkup_drop_zone_access_points" {}
variable "tna_backup_inventory_arn" {}

##
# backup target bucket allowing access through access points
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "tna_backup_drop_zone" {
    bucket = "tna-backup-drop-zone"

    force_destroy = false

    tags = merge(
        var.default_tags,
        {
            Name = "tna-backup-drop-zone"
        }
    )
}

resource "aws_s3_bucket_ownership_controls" "tna_backup_drop_zone" {
    bucket = aws_s3_bucket.tna_backup_drop_zone.id

    rule {
        object_ownership = "BucketOwnerEnforced"
    }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tna_backup_drop_zone" {
    bucket = aws_s3_bucket.tna_backup_drop_zone.id

    rule {
        apply_server_side_encryption_by_default {
            sse_algorithm = "AES256"
        }
        bucket_key_enabled = true
    }
}

resource "aws_s3_bucket_public_access_block" "tna_backup_drop_zone" {
    bucket = aws_s3_bucket.tna_backup_drop_zone.id

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
}

resource "aws_s3_bucket_inventory" "tna_backup_drop_zone" {
    bucket = aws_s3_bucket.tna_backup_drop_zone.id
    name   = "EntireBucketDaily"

    included_object_versions = "All"

    schedule {
        frequency = "Weekly"
    }

    destination {
        bucket {
            format     = "CSV"
            bucket_arn = var.tna_backup_inventory_arn
        }
    }
}

resource "aws_s3_bucket_policy" "tna_backup_drop_zone_access_from_another_account" {
    bucket = aws_s3_bucket.tna_backup_drop_zone.id
    policy = file("${path.root}/s3/templates/tna-backup-drop-zone-bucket-policy.json")
}

resource "aws_s3_access_point" "backup_drop_zone_access_point" {
    for_each = {for k in var.bkup_drop_zone_access_points : k.ap_name => k}
    bucket   = aws_s3_bucket.tna_backup_drop_zone.id
    name     = each.value.ap_name

    public_access_block_configuration {
        block_public_acls       = true
        block_public_policy     = false
        ignore_public_acls      = true
        restrict_public_buckets = false
    }

    lifecycle {
        ignore_changes = [policy]
    }
}

resource "aws_s3control_access_point_policy" "drop_zone_ap_policy" {
    for_each         = {for k in var.bkup_drop_zone_access_points : k.ap_name => k}
    access_point_arn = aws_s3_access_point.backup_drop_zone_access_point["${each.value.ap_name}"].arn

    policy = templatefile("${path.root}/s3/templates/backup-drop-zone-access-point-policy.json", {
        ap_name   = each.value.ap_name,
        ap_path   = each.value.ap_path,
        actions   = each.value.actions,
        role_arns = each.value.role_arns
    })
}

output "tna_backup_drop_zone_arn" {
    value = aws_s3_bucket.tna_backup_drop_zone.arn
}

output "tna_backup_drop_zone_name" {
    value = aws_s3_bucket.tna_backup_drop_zone.bucket
}

output "tna_backup_drop_zone_id" {
    value = aws_s3_bucket.tna_backup_drop_zone.id
}
