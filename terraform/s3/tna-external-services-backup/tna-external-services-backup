variable "default_tags" {}
variable "tna_backup_inventory_arn" {}

##
# backup for backups of external services such as GitHub, Slack, Jira
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "tna_external_services_backup" {
    bucket = "tna-external-services-backup"

    force_destroy = false

    tags = merge(
        var.default_tags,
        {
            Name = "tna-external-services-backup"
        }
    )
}

resource "aws_s3_bucket_ownership_controls" "tna_external_services_backup" {
    bucket = aws_s3_bucket.tna_external_services_backup.id

    rule {
        object_ownership = "BucketOwnerEnforced"
    }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tna_external_services_backup" {
    bucket = aws_s3_bucket.tna_external_services_backup.id

    rule {
        apply_server_side_encryption_by_default {
            sse_algorithm = "AES256"
        }
        bucket_key_enabled = true
    }
}

resource "aws_s3_bucket_public_access_block" "tna_external_services_backup" {
    bucket = aws_s3_bucket.tna_external_services_backup.id

    block_public_acls       = false
    block_public_policy     = false
    ignore_public_acls      = false
    restrict_public_buckets = false
}

resource "aws_s3_bucket_versioning" "tna_external_services_backup" {
    bucket = aws_s3_bucket.tna_external_services_backup.id

    versioning_configuration {
        status = "Enabled"
    }
}

resource "aws_s3_bucket_inventory" "tna_external_services_backup" {
    bucket = aws_s3_bucket.tna_external_services_backup.id
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

output "tna_external_services_backup_arn" {
    value = aws_s3_bucket.tna_external_services_backup.arn
}

output "tna_external_services_backup_name" {
    value = aws_s3_bucket.tna_external_services_backup.bucket
}

output "tna_external_services_backup_id" {
    value = aws_s3_bucket.tna_external_services_backup.id
}
