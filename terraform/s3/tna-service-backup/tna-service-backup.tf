variable "default_tags" {}
variable "tna_backup_inventory_arn" {}

##
# this bucket is used by ec2 instances which download data from non-TNA service
# such as GitHub
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "tna_service_backup" {
    bucket = "tna-service-backup"

    force_destroy = false

    tags = merge(
        var.default_tags,
        {
            Name = "tna-service-backup"
        }
    )
}

resource "aws_s3_bucket_ownership_controls" "tna_service_backup" {
    bucket = aws_s3_bucket.tna_service_backup.id

    rule {
        object_ownership = "BucketOwnerEnforced"
    }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tna_service_backup" {
    bucket = aws_s3_bucket.tna_service_backup.id

    rule {
        apply_server_side_encryption_by_default {
            sse_algorithm = "AES256"
        }
    }
}

resource "aws_s3_bucket_public_access_block" "tna_service_backup" {
    bucket = aws_s3_bucket.tna_service_backup.id

    block_public_acls       = false
    block_public_policy     = false
    ignore_public_acls      = false
    restrict_public_buckets = false
}

resource "aws_s3_bucket_inventory" "tna_service_backup" {
  bucket = aws_s3_bucket.tna_service_backup.id
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
