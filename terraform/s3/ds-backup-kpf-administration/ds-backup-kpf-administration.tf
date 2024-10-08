variable "default_tags" {}

##
# this bucket is used for key pairs
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "ds_backup_kpf_administration" {
    bucket = "ds-backup-kpf-administration"

    force_destroy = false

    tags = merge(
        var.default_tags,
        {
            Name = "ds-backup-kpf-administration"
        }
    )
}

resource "aws_s3_bucket_ownership_controls" "ds_backup_kpf_administration" {
    bucket = aws_s3_bucket.ds_backup_kpf_administration.id

    rule {
        object_ownership = "BucketOwnerEnforced"
    }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "ds_backup_kpf_administration" {
    bucket = aws_s3_bucket.ds_backup_kpf_administration.id

    rule {
        apply_server_side_encryption_by_default {
            sse_algorithm = "AES256"
        }
    }
}

resource "aws_s3_bucket_public_access_block" "ds_backup_kpf_administration" {
    bucket = aws_s3_bucket.ds_backup_kpf_administration.id

    block_public_acls       = false
    block_public_policy     = false
    ignore_public_acls      = false
    restrict_public_buckets = false
}
