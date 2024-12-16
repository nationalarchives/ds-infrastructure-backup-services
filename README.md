# ds-infrastructure-backup-services

## Prerequisites

### Dependencies
Terraform from repository _ds-infrastructure-backup_ need to be applied before
this repository can be applied successfully.

In _ds-infrastructure-databases_ using GitHub Actions the EBS for database servers and database servers mysql-main-prime and mysql-main-replica need to be
created before terraform apply. \
Building the AMIs using the GitHub Actions for instances need to be prepared

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

### Status of records
#### object_checkins
0 - new record
1 - queued
2 - in progress
3 - ingested
4 - doubled up; redundant; switch old record from 0 to 4
5 - doubled up; redundant; switch new record; because status 1 or 2;
8 - file doesn't exist
9 - queue entry error
#### queues
0 - new record
1 - picked up by copying process
2 - finished
4, 5, 8, 9 - indicating check wasn't as expected
#### object_copies
0 - new record
1 - copying in progress
2 - finished
9 - error



