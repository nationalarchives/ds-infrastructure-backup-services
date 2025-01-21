resource "aws_iam_policy" "attach_ebs_volume_policy" {
    name        = "attach-ebs-volume-policy"
    description = "attach and detach ebs volumes"

    policy = file("${path.root}/templates/attach-ebs-volume-policy.json")
}

resource "aws_iam_policy" "ec2_drop_zone_policy" {
    name        = "ec2-drop-zone-policy"
    description = "allow ec2 access to s3 drop zone bucket"
    policy = templatefile("${path.module}/templates/ec2-drop-zone-policy.json", {
        queue_arns = jsonencode(var.queue_arns)
    })
}

resource "aws_iam_policy" "tna_services_bkup_github" {
    name        = "tna-services-bkup-github"
    description = "allow ec2 access to access point s3 drop zone bucket"
    policy = file("${path.module}/templates/tna-services-bkup-github-policy.json")
}
