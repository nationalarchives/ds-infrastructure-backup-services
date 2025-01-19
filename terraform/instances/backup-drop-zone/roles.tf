terraform {
    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = "5.54.1"
        }
    }
}
resource "aws_iam_role" "ec2_drop_zone_role" {
    name = "drop-zone-ec2-role"
    assume_role_policy = file("${path.module}/templates/ec2_assume_role.json")
    tags = var.tags
}

resource "aws_iam_instance_profile" "ec2_drop_zone_profile" {
    name = "drop-zone-ec2-role"
    role = aws_iam_role.ec2_drop_zone_role.name
    tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ec2_ssm" {
    role       = aws_iam_role.ec2_drop_zone_role.name
    policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "ec2_asm_ssm" {
    role       = aws_iam_role.ec2_drop_zone_role.name
    policy_arn = aws_iam_policy.ec2_asm_ssm_access.arn
}

resource "aws_iam_role_policy_attachment" "ec2_sqs" {
    role       = aws_iam_role.ec2_drop_zone_role.name
    policy_arn = aws_iam_policy.ec2_sqs_access.arn
}

resource "aws_iam_role_policy_attachment" "ec2_s3" {
    role       = aws_iam_role.ec2_drop_zone_role.name
    policy_arn = aws_iam_policy.ec2_s3_access.arn
}
