resource "aws_iam_policy" "attach_ebs_volume_policy" {
    name        = "attach-ebs-volume-policy"
    description = "attach and detach ebs volumes"

    policy = file("${path.root}/templates/attach-ebs-volume-policy.json")
}
