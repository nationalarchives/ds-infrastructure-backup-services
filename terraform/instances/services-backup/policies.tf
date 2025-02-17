resource "aws_iam_policy" "ap_access_policy" {
    name        = "tna-services-backup-ap-access-policy"
    description = "access to access point for ec2"

    policy = file("${path.module}/templates/ap-access-policy.json")
}
