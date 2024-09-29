variable "default_tags" {}
variable "tna_backup_inventory_arn" {}

##
# backup final destination
# all objects come from tna-backup-intake and should have the correct
# retention settings
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "tna_backup_vault" {
    bucket = "tna-backup-vault"

    force_destroy       = false
    object_lock_enabled = true

    tags = merge(
        var.default_tags,
        {
            Name = "tna-backup-vault"
        }
    )
}

resource "aws_s3_bucket_ownership_controls" "tna_backup_vault" {
    bucket = aws_s3_bucket.tna_backup_vault.id

    rule {
        object_ownership = "BucketOwnerEnforced"
    }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tna_backup_vault" {
    bucket = aws_s3_bucket.tna_backup_vault.id

    rule {
        apply_server_side_encryption_by_default {
            sse_algorithm = "AES256"
        }
        bucket_key_enabled = true
    }
}

resource "aws_s3_bucket_public_access_block" "tna_backup_vault" {
    bucket = aws_s3_bucket.tna_backup_vault.id

    block_public_acls       = false
    block_public_policy     = false
    ignore_public_acls      = false
    restrict_public_buckets = false
}

resource "aws_s3_bucket_versioning" "tna_backup_vault" {
    bucket = aws_s3_bucket.tna_backup_vault.id

    versioning_configuration {
        status = "Enabled"
    }
}

resource "aws_s3_bucket_inventory" "tna_backup_vault" {
    bucket = aws_s3_bucket.tna_backup_vault.id
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
