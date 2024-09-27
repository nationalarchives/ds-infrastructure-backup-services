##
# this bucket records the bucket inventories
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "tna_backup_inventory" {
    bucket = "tna-backup-inventory"

    force_destroy = true

    tags = merge(
        var.default_tags,
        {
            Name = "tna-backup-inventory"
        }
    )
}

resource "aws_s3_bucket_ownership_controls" "tna_backup_inventory" {
    bucket = aws_s3_bucket.tna_service_backup.id

    rule {
        object_ownership = "BucketOwnerEnforced"
    }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tna_backup_inventory" {
    bucket = aws_s3_bucket.tna_service_backup.id

    rule {
        apply_server_side_encryption_by_default {
            sse_algorithm = "AES256"
        }
    }
}

resource "aws_s3_bucket_public_access_block" "tna_backup_inventory" {
    bucket = aws_s3_bucket.tna_service_backup.id

    block_public_acls       = false
    block_public_policy     = false
    ignore_public_acls      = false
    restrict_public_buckets = false
}
