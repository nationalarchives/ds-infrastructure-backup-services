variable "default_tags" {}

##
# this bucket records the buvket inventories
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "tna_backup_tooling" {
    bucket = "tna-backup-tooling"

    force_destroy = true

    tags = merge(
        var.default_tags,
        {
            Name = "tna-backup-tooling"
        }
    )
}

resource "aws_s3_bucket_ownership_controls" "tna_backup_tooling" {
    bucket = aws_s3_bucket.tna_backup_tooling.id

    rule {
        object_ownership = "BucketOwnerEnforced"
    }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tna_backup_tooling" {
    bucket = aws_s3_bucket.tna_backup_tooling.id

    rule {
        apply_server_side_encryption_by_default {
            sse_algorithm = "AES256"
        }
    }
}

resource "aws_s3_bucket_public_access_block" "tna_backup_tooling" {
    bucket = aws_s3_bucket.tna_backup_tooling.id

    block_public_acls       = false
    block_public_policy     = false
    ignore_public_acls      = false
    restrict_public_buckets = false
}
