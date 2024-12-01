locals {
    default_tags = {
        Owner      = "Digital Services"
        CostCentre = "Digital Services"
        Region     = var.region
        Account    = var.account_id
        Terraform  = "true"
        Repository = "ds-infrastructure-backup-services"
    }

    vpc_info = jsondecode(data.aws_ssm_parameter.vpc_info.value)
    public_subnet_a_info = jsondecode(data.aws_ssm_parameter.public_subnet_a_info.value)
    private_subnet_a_info = jsondecode(data.aws_ssm_parameter.private_subnet_a_info.value)
}

variable "account_id" {
    default = "637423167251"
}

variable "region" {
    default = "eu-west-2"
}
