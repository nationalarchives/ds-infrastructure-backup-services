terraform {
    backend "s3" {
        bucket = "ds-terraform-state-eu-west-2-637423167251"
        key    = "ds-infrastructure-backup-services/terraform.tfstate"
        region = "eu-west-2"
    }
}

provider "aws" {
    region = "eu-west-2"
}
