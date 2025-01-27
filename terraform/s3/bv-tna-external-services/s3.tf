variable "default_tags" {}
variable "tna_backup_inventory_arn" {}

##
# backup vault collecting backups for Digital Services
# retention settings
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "bv_tna_external_services" {
    bucket = "bv-tna-external-services"

    force_destroy       = false
    object_lock_enabled = true

    tags = merge(
        var.default_tags,
        {
            Name = "bv-tna-external-services"
        }
    )
}

resource "aws_s3_bucket_ownership_controls" "bv_tna_external_services" {
    bucket = aws_s3_bucket.bv_tna_external_services.id

    rule {
        object_ownership = "BucketOwnerEnforced"
    }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bv_tna_external_services" {
    bucket = aws_s3_bucket.bv_tna_external_services.id

    rule {
        apply_server_side_encryption_by_default {
            sse_algorithm = "AES256"
        }
        bucket_key_enabled = true
    }
}

resource "aws_s3_bucket_public_access_block" "bv_tna_external_services" {
    bucket = aws_s3_bucket.bv_tna_external_services.id

    block_public_acls       = false
    block_public_policy     = false
    ignore_public_acls      = false
    restrict_public_buckets = false
}

resource "aws_s3_bucket_versioning" "bv_tna_external_services" {
    bucket = aws_s3_bucket.bv_tna_external_services.id

    versioning_configuration {
        status = "Enabled"
    }
}

resource "aws_s3_bucket_inventory" "bv_tna_external_services" {
    bucket = aws_s3_bucket.bv_tna_external_services.id
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
