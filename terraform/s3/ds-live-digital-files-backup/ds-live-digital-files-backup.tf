variable "default_tags" {}
variable "tna_backup_inventory_arn" {}

##
# backup final destination
# all objects come from tna-backup-intake and should have the correct
# retention settings
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "ds_live_digital_files_backup" {
    bucket = "ds-live-digital-files-backup"

    force_destroy       = false
    object_lock_enabled = true

    tags = merge(
        var.default_tags,
        {
            Name = "ds-live-digital-files-backup"
        }
    )
}

resource "aws_s3_bucket_ownership_controls" "ds_live_digital_files_backup" {
    bucket = aws_s3_bucket.ds_live_digital_files_backup.id

    rule {
        object_ownership = "BucketOwnerEnforced"
    }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "ds_live_digital_files_backup" {
    bucket = aws_s3_bucket.ds_live_digital_files_backup.id

    rule {
        apply_server_side_encryption_by_default {
            sse_algorithm = "AES256"
        }
        bucket_key_enabled = true
    }
}

resource "aws_s3_bucket_public_access_block" "ds_live_digital_files_backup" {
    bucket = aws_s3_bucket.ds_live_digital_files_backup.id

    block_public_acls       = false
    block_public_policy     = false
    ignore_public_acls      = false
    restrict_public_buckets = false
}

resource "aws_s3_bucket_versioning" "ds_live_digital_files_backup" {
    bucket = aws_s3_bucket.ds_live_digital_files_backup.id

    versioning_configuration {
        status = "Enabled"
    }
}

resource "aws_s3_bucket_inventory" "ds_live_digital_files_backup" {
    bucket = aws_s3_bucket.ds_live_digital_files_backup.id
    name   = "EntireBucketWeekly"

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
