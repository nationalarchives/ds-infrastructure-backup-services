resource "aws_iam_policy" "ec2_s3_access" {
    name        = "drop-zone-ec2-s3-access-policy"
    description = "drop-zone access to all s3 buckets"

    policy = file("${path.module}/templates/ec2-s3-access-policy.json")
}

resource "aws_iam_policy" "ec2_asm_ssm_access" {
    name        = "drop-zone-ec2-asm-ssm-access-policy"
    description = "drop-zone access to secrets and parameters"

    policy = file("${path.module}/templates/ec2-asm-ssm-access-policy.json")
}

resource "aws_iam_policy" "ec2_sqs_access" {
    name        = "drop-zone-ec2-sqs-access-policy"
    description = "drop-zone access to sqs"

    policy = file("${path.module}/templates/ec2-sqs-access-policy.json")
}
