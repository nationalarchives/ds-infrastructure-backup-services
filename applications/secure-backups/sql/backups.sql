PZF+eLLptZ?no81Kj9]}C:VBdh4Wu

# setup of user
#
CREATE USER 'checkin_user'@'localhost' IDENTIFIED BY 's-VF!5R1Z!yzX6B61)du';
GRANT INSERT, UPDATE, SELECT on backups.* TO 'checkin_user'@'localhost' WITH GRANT OPTION;
CREATE USER 'checkin_user'@'192.168.2.0/255.255.254.0' IDENTIFIED BY 's-VF!5R1Z!yzX6B61)du';
GRANT INSERT, UPDATE, SELECT on backups.* TO 'checkin_user'@'192.168.2.0/255.255.254.0' WITH GRANT OPTION;
FLUSH PRIVILEGES;

# set up of database
#
CREATE SCHEMA `backups`;

CREATE TABLE `backups`.`object_checkins` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `queue_id` BIGINT UNSIGNED NULL,
  `copy_id` BIGINT UNSIGNED NULL,
  `bucket` VARCHAR(63) NOT NULL,
  `object_key` VARCHAR(1024) NOT NULL,
  `object_name` VARCHAR(1024) NOT NULL,
  `object_size` BIGINT NULL,
  `object_type` VARCHAR(256) NULL,
  `kms_key_arn` VARCHAR(2048) NULL,
  `source_account_id` VARCHAR(12) NULL,
  `etag` VARCHAR(256) NOT NULL,
  `expires_string` VARCHAR(256) NULL,
  `checksum_crc32` CHAR(8) NULL,
  `checksum_crc32c` CHAR(10) NULL,
  `checksum_sha1` CHAR(40) NULL,
  `checksum_sha256` CHAR(64) NULL,
  `serverside_encryption` CHAR(64) NULL,
  `sse_customer_algorithm` VARCHAR(256) NULL,
  `sse_customer_key_md5` VARCHAR(256) NULL,
  `sse_kms_key_id` VARCHAR(256) NULL,
  `last_modified` VARCHAR(64) NULL,
  `retain_until_date` VARCHAR(45) NULL,
  `lock_mode` VARCHAR(45) NULL,
  `legal_hold` VARCHAR(45) NULL,
  `received_ts` FLOAT NULL,
  `finished_ts` FLOAT NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  `status` TINYINT UNSIGNED NULL,
  PRIMARY KEY (`id`));

CREATE TABLE `backups`.`queues` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `checkin_id` BIGINT UNSIGNED NULL,
  `copy_id` BIGINT UNSIGNED NULL,
  `message_id` VARCHAR(100) NULL,
  `md5_of_message_body` CHAR(32) NULL,
  `md5_of_message_attributes` CHAR(32) NULL,
  `md5_of_message_system_attributes` CHAR(32) NULL,
  `sequence_number` CHAR(32) NULL,
  `kms_key_arn` VARCHAR(2048) NULL,
  `source_account_id` VARCHAR(12) NULL,
  `received_ts` FLOAT NULL,
  `finished_ts` FLOAT NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  `status` TINYINT UNSIGNED NULL,
  INDEX (`message_id`),
  PRIMARY KEY (`id`));

CREATE TABLE `backups`.`object_copies` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `queue_id` BIGINT UNSIGNED NULL,
  `checkin_id` BIGINT UNSIGNED NULL,
  `object_name` VARCHAR(1024) NOT NULL,
  `source_name` VARCHAR(1024) NOT NULL,
  `bucket` VARCHAR(63) NOT NULL,
  `access_point` VARCHAR(50) NULL,
  `object_key` VARCHAR(1024) NOT NULL,
  `object_size` BIGINT NULL,
  `object_type` VARCHAR(256) NULL,
  `upload_id` VARCHAR(256) NULL,
  `version_id` VARCHAR(256) NULL,
  `kms_key_arn` VARCHAR(2048) NULL,
  `source_account_id` VARCHAR(12) NULL,
  `etag` VARCHAR(256) NOT NULL,
  `expiration` VARCHAR(256) NULL,
  `server_side_encryption` VARCHAR(12) NULL,
  `sse_customer_algorithm` VARCHAR(256) NULL,
  `sse_customer_key_md5` VARCHAR(256) NULL,
  `sse_kms_key_id` VARCHAR(256) NULL,
  `checksum_crc32` CHAR(8) NULL,
  `checksum_crc32c` CHAR(10) NULL,
  `checksum_sha1` CHAR(40) NULL,
  `checksum_sha256` CHAR(64) NULL,
  `last_modified` VARCHAR(64) NULL,
  `retain_until_date` VARCHAR(45) NULL,
  `lock_mode` VARCHAR(45) NULL,
  `legal_hold` VARCHAR(45) NULL,
  `percentage` DECIMAL(6,2) NULL,
  `received_ts` FLOAT NULL,
  `finished_ts` FLOAT NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  `status` TINYINT UNSIGNED NULL,
  PRIMARY KEY (`id`));

CREATE TABLE `backups`.`ap_targets` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `access_point` VARCHAR(50) NOT NULL,
  `bucket` VARCHAR(63) NOT NULL,
  `name_processing` TINYINT UNSIGNED DEFAULT 0,
  `source_account_id` VARCHAR(12) NULL,
  `kms_key_arn` VARCHAR(2048) NULL,
  `storage_class` VARCHAR(80) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  `status` TINYINT UNSIGNED NULL,
  PRIMARY KEY (`id`),
  INDEX(`access_point`));

INSERT INTO ap_targets (access_point, bucket, name_processing, source_account_id, created_at, status) VALUES ("github-backup", "tna-external-services-backup", 1, "968803923593", NOW(), 1);
INSERT INTO ap_targets (access_point, bucket, name_processing, source_account_id, created_at, status) VALUES ("ds-databases-backup", "tna-databases-backup",1, "968803923593", NOW(), 1);
INSERT INTO ap_targets (access_point, bucket, name_processing, source_account_id, created_at, status) VALUES ("ds-digital-files-backup", "ds-digital-files-backup", 0, "968803923593", NOW(), 1);

CREATE TABLE `backups`.`part_uploads` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `checkin_id` BIGINT UNSIGNED NOT NULL,
  `copy_id` BIGINT UNSIGNED NOT NULL,
  `source_bucket` VARCHAR(63) NOT NULL,
  `source_key` VARCHAR(1024) NOT NULL,
  `access_point` VARCHAR(50) NOT NULL,
  `target_bucket` VARCHAR(63) NOT NULL,
  `target_key` VARCHAR(1024) NOT NULL,
  `kms_key_arn` VARCHAR(2048) NULL,
  `source_account_id` VARCHAR(12) NULL,
  `retain_until_date` VARCHAR(45) NULL,
  `lock_mode` VARCHAR(45) NULL,
  `legal_hold` VARCHAR(45) NULL,
  `content_length` BIGINT NOT NULL,
  `byte_range` VARCHAR(128) NOT NULL,
  `part` INT NOT NULL,
  `percentage` DECIMAL(6,2) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  `status` TINYINT UNSIGNED NULL,
  PRIMARY KEY (`id`));

CREATE TABLE `backups`.`queue_status` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `queue_name` VARCHAR(100) NOT NULL,
  `queue_arn` VARCHAR(120) NOT NULL,
  `queue_length` INT UNSIGNED NULL,
  `created_at` DATETIME NULL,
  `status` TINYINT UNSIGNED NULL,
  PRIMARY KEY (`id`),
  INDEX(`queue_name`),
  INDEX(`queue_arn`));

CREATE TABLE `backups`.`object_tags` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `source_id` BIGINT UNSIGNED NOT NULL,
  `source_type` VARCHAR(64) NOT NULL,
  `object_key` VARCHAR(1024) NOT NULL,
  `tag_key` VARCHAR(128) NOT NULL,
  `tag_value` VARCHAR(256) NULL,
  `tag_type` VARCHAR(25) NOT NULL,
  `created_at` DATETIME NULL,
  `status` TINYINT UNSIGNED NULL,
  PRIMARY KEY (`id`));
