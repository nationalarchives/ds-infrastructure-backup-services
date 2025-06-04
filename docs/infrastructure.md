## Infrastructure
### Overview
The infrastructure and applications are designed to monitor and handle incoming files 24x7. \
Access permissions are limited to very few personal and the restoration process is manual to mitigate manipulation of files. Files stored in this account are shield from accidental ot malicious overwriting. An exception are areas in which files are updated or deleted frequently and might not be irreplaceable or hard to reproduce, however, the target buckets are versioned and it is possible to role back any changes or deletions.\
### Components
- S3 - The S3 buckets are used to receive incoming files from other accounts and to move those received files to a configured area (S3).
- EC2 - The EC2 instances are used to run the applications that process the incoming files, monitor the instances and queues, and record the processing results in a database.
- Lambda - The Lambda functions are used to trigger the applications when new files are received in S3.
- SQS - The SQS queues are used to handle the incoming files and to trigger the applications when new files are received in S3.
- Applications - Several applications, coded in Python responsible to process the backups
### Backup and Recovery
#### Incoming Files
Incoming files are stored in an S3 bucket (tna-backup-drop-zone). This S3 bucket exposes entry points from other Access from other accounts over access points. \
These access points are account and purpose specific. \
When the Lambda function is triggered, it moves the file to the configured areas (S3) and deletes the file from the incoming files bucket. \
It is possible to extend the incoming files bucket to further S3 buckets to suit the need to separate files and non-shared destinations. \
Target destinations can be configured with lifecycle rules and retention definitions to ensure the correct retention policies are applied. \
If no target is defined, the file is moved to a standard S3 bucket (bv-tna-backup-vault).
#### Processing Files
The process of incoming files is sequenced and processed following the configured destiation and steered by meta data attached to the files. \
This allows a flexible approach to handle ad hoc requests.
#### Lifecycle, Retention and Deletion
Any lifecycle rules and retention policies for S3 buckets should be set individually for each bucket and purpose of the backed up files. \
These are dependent on the business needs and data types. Files which are irreplaceable should have the highest retention settings with a review after a set period of time. \
Database backups need to be retained for a minimum of 90 days, but for forensic reasons, it is recommended to retain them for at least 180 days. \
