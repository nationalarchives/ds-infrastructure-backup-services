Content-Type: multipart/mixed; boundary="//"
MIME-Version: 1.0

--//
Content-Type: text/cloud-config; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="cloud-config.txt"

#cloud-config
cloud_final_modules:
- [scripts-user, always]

--//
Content-Type: text/x-shellscript; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="userdata.txt"

#!/bin/bash

sudo touch /var/log/start-up.log

echo "$(date '+%Y-%m-%d %T') - system update" | sudo tee -a /var/log/start-up.log > /dev/null
sudo dnf -y update

service_status=sudo systemctl is-active watch_sftp_dir.service

# service status is inactive if not enabled, disabled or not started
if [[ "$service_status" = "inactive" ]]; then
  sudo systemctl enable watch_sftp_dir.service
  sudo systemctl start watch_sftp_dir.service
el [[ "$service_status" = "failed" ]]
  sudo systemctl restart watch_sftp_dir.service
fi

--//--
