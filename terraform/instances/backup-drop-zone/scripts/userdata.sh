#!/bin/bash

# write environment variable for all profiles to /etc/profile.d/*.sh
sudo cat <<FILE >/etc/profile.d/secure-backups.sh
# environment variables for secure-backups service
export SSM_ID='{ssm_id}'
FILE
# ensure backup service is enabled and active
