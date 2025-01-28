resource "aws_iam_policy" "s3_access_policy" {
    name        = "tna-services-backup-s3-access-policy"
    description = "access to s3 for ec2"

    policy = file("${path.module}/templates/s3-accesss-policy.json")
}

resource "aws_iam_policy" "ap_access_policy" {
    name        = "tna-services-backup-ap-access-policy"
    description = "access to access point for ec2"

    policy = file("${path.module}/templates/ap-access-policy.json")
}
