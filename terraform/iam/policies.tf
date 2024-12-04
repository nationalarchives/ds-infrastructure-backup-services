terraform {
    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = "5.54.1"
        }
    }
}
resource "aws_iam_policy" "attach_ebs_volume_policy" {
    name        = "attach-ebs-volume-policy"
    description = "attach and detach ebs volumes"

    policy = file("${path.root}/templates/attach-ebs-volume-policy.json")
}


resource "aws_iam_policy" "ec2_drop_zone_policy" {
    name        = "ec2-drop-zone-policy"
    description = "allow ec2 access to s3 drop zone bucket"
    policy = file("${path.module}/templates/ec2-drop-zone-policy.json")
}
