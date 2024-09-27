# ds-infrastructure-backup-services

## Prerequisites

### Dependencies
Terraform from repository _ds-infrastructure-backup_ need to be applied before
this repository can be applied successfully.

In _ds-infrastructure-databases_ using GitHub Actions the EBS for database servers and database servers mysql-main-prime and mysql-main-replica need to be
created before terraform apply. \
Building the AMIs using the GitHub Actions for instances need to be prepared

### SSM - parameter store
Parameter _/infrastructure/network/client_vpn_cidr_ need to be updated to allow
access using the Client VPN connection

### ASM - secrets
Secret _/infrastructure/credentials/mysql-backup_ need to be added before building the database servers. \
structure of the secrets is:
```text
{
    "root_password":"password",
    "admin_user":"name",
    "admin_password":"password",
    "repl_user":"name",
    "repl_password":"pasword",
    "bkup_user":"name",
    "bkup_password":"password",
    "network_cidr":"cidr-of-subnet"
}
```
