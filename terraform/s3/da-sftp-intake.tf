##
# this bucket is used by ec2 instance which allows users to transfer files using
# SFTP
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "da_sftp_intake" {
    bucket = "da-sftp-intake"

    force_destroy = true

    tags = merge(
        var.default_tags,
        {
            Name = "da-sftp-intake"
        }
    )
}

resource "aws_s3_bucket_ownership_controls" "da_sftp_intake" {
    bucket = aws_s3_bucket.da_sftp_intake.id

    rule {
        object_ownership = "BucketOwnerEnforced"
    }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "da_sftp_intake" {
    bucket = aws_s3_bucket.da_sftp_intake.id

    rule {
        apply_server_side_encryption_by_default {
            sse_algorithm = "AES256"
        }
    }
}

#resource "aws_s3_bucket_object_lock_configuration" "da_sftp_intake" {
#    bucket = aws_s3_bucket.da_sftp_intake.id
#
#    rule {
#        default_retention {
#            mode = "COMPLIANCE"
#            days = 60
#        }
#    }
#}

resource "aws_s3_bucket_public_access_block" "da_sftp_intake" {
    bucket = aws_s3_bucket.da_sftp_intake.id

    block_public_acls       = false
    block_public_policy     = false
    ignore_public_acls      = false
    restrict_public_buckets = false
}
