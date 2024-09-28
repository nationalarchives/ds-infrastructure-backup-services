data "aws_ami" "service_backups" {
    most_recent = true
    filter {
        name = "name"
        values = [
            "service-backups-primer*"
        ]
    }
    filter {
        name = "virtualization-type"
        values = [
            "hvm"
        ]
    }
    owners = [
        data.aws_caller_identity.current.account_id,
    ]
}

data "aws_ami" "da_sftp_x_posts" {
    most_recent = true
    filter {
        name = "name"
        values = [
            "da-x-posts-backup-primer*"
        ]
    }
    filter {
        name = "virtualization-type"
        values = [
            "hvm"
        ]
    }
    owners = [
        data.aws_caller_identity.current.account_id,
    ]
}

data "aws_ami" "backup_intake" {
    most_recent = true
    filter {
        name = "name"
        values = [
            "backup-intake-primer*"
        ]
    }
    filter {
        name = "virtualization-type"
        values = [
            "hvm"
        ]
    }
    owners = [
        data.aws_caller_identity.current.account_id,
    ]
}

data "aws_ami" "mysql_main_ami" {
    most_recent = true
    filter {
        name   = "name"
        values = [
            "mysql-main-primer-*"
        ]
    }
    filter {
        name   = "virtualization-type"
        values = [
            "hvm"
        ]
    }
    owners = [
        data.aws_caller_identity.current.account_id,
    ]
}
