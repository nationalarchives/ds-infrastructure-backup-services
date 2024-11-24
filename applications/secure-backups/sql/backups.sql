# setup of user
#
CREATE USER 'checkin_user'@'localhost' IDENTIFIED BY 's-VF!5R1Z!yzX6B61)du';
GRANT INSERT, UPDATE, SELECT on backups.* TO 'checkin_user'@'localhost' WITH GRANT OPTION;
CREATE USER 'checkin_user'@'192.168.2.0/255.255.254.0' IDENTIFIED BY 's-VF!5R1Z!yzX6B61)du';
GRANT INSERT, UPDATE, SELECT on backups.* TO 'checkin_user'@'192.168.2.0/255.255.254.0' WITH GRANT OPTION;
FLUSH PRIVILEGES;

# set up of database
#
CREATE SCHEMA `backups` ;

CREATE TABLE `backups`.`object_checkins` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `queue_id` BIGINT UNSIGNED NULL,
  `copy_id` BIGINT UNSIGNED NULL,
  `bucket_name` VARCHAR(63) NOT NULL,
  `object_key` VARCHAR(1024) NOT NULL,
  `object_size` BIGINT NULL,
  `object_type` VARCHAR(256) NULL,
  `version_id` VARCHAR(256) NULL,
  `etag` VARCHAR(256) NOT NULL,
  `expires_string` VARCHAR(256)NULL,
  `checksum_crc32` CHAR(8) NULL,
  `checksum_crc32c` CHAR(10) NULL,
  `checksum_sha1` CHAR(40) NULL,
  `checksum_sha256` CHAR(64) NULL,
  `serverside_encryption` CHAR(64) NULL,
  `storage_class` CHAR(45) NULL,
  `last_modified` VARCHAR(64) NULL,
  `retain_until_date` VARCHAR(45) NULL,
  `lock_mode` VARCHAR(45) NULL,
  `legal_hold` VARCHAR(45) NULL,
  `received_ts` CHAR(18) NULL,
  `finished_ts` CHAR(18) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  `status` INT NULL,
  PRIMARY KEY (`id`));



CREATE TABLE `backups`.`object_checkins` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `queue_id` BIGINT UNSIGNED NULL,
  `copy_id` BIGINT UNSIGNED NULL,
  `object_name` VARCHAR(1024) NOT NULL,
  `object_size` BIGINT NULL,
  `object_type` VARCHAR(256) NULL,
  `bucket` VARCHAR(63) NOT NULL,
  `object_key` VARCHAR(1024) NOT NULL,
  `etag` VARCHAR(256) NOT NULL,
  `checksum_crc32` CHAR(8) NULL,
  `checksum_crc32c` CHAR(10) NULL,
  `checksum_sha1` CHAR(40) NULL,
  `checksum_sha256` CHAR(64) NULL,
  `last_modified` VARCHAR(64) NULL,
  `retain_until_date` VARCHAR(45) NULL,
  `lock_mode` VARCHAR(45) NULL,
  `legal_hold` VARCHAR(45) NULL,
  `received_ts` CHAR(18) NULL,
  `finished_ts` CHAR(18) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  `status` INT NULL,
  PRIMARY KEY (`id`));

CREATE TABLE `backups`.`queues` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `checkin_id` BIGINT UNSIGNED NULL,
  `copy_id` BIGINT UNSIGNED NULL,
  `message_id` VARCHAR(100) NOT NULL,
  `md5_of_message_body` CHAR(32) NULL,
  `md5_of_message_attributes` CHAR(32) NULL,
  `md5_of_message_system_attributes` CHAR(32) NULL,
  `sequence_number` CHAR(32) NOT NULL,
  `received_ts` CHAR(18) NULL,
  `finished_ts` CHAR(18) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  `status` INT NULL,
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
  `etag` VARCHAR(256) NOT NULL,
  `checksum_crc32` CHAR(8) NULL,
  `checksum_crc32c` CHAR(10) NULL,
  `checksum_sha1` CHAR(40) NULL,
  `checksum_sha256` CHAR(64) NULL,
  `last_modified` VARCHAR(64) NULL,
  `retain_until_date` VARCHAR(45) NULL,
  `lock_mode` VARCHAR(45) NULL,
  `legal_hold` VARCHAR(45) NULL,
  `percentage` DECIMAL(6,2) NULL,
  `received_ts` CHAR(18) NULL,
  `finished_ts` CHAR(18) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  `status` INT NULL,
  PRIMARY KEY (`id`));

CREATE TABLE `backups`.`ap_targets` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `access_point` VARCHAR(50) NOT NULL,
  `bucket` VARCHAR(63) NOT NULL,
  `name_processing` TINYINT UNSIGNED DEFAULT 0,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  `status` INT NULL,
  PRIMARY KEY (`id`),
  INDEX(`access_point`));

CREATE TABLE `backups`.`part_uploads` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `checkin_id` BIGINT UNSIGNED NOT NULL,
  `copy_id` BIGINT UNSIGNED NOT NULL,
  `source_bucket` VARCHAR(63) NOT NULL,
  `source_key` VARCHAR(1024) NOT NULL,
  `access_point` VARCHAR(50) NOT NULL,
  `target_bucket` VARCHAR(63) NOT NULL,
  `target_key` VARCHAR(1024) NOT NULL,
  `retain_until_date` VARCHAR(45) NULL,
  `lock_mode` VARCHAR(45) NULL,
  `legal_hold` VARCHAR(45) NULL,
  `content_length` BIGINT NOT NULL,
  `byte_range` VARCHAR(128) NOT NULL,
  `part` INT NOT NULL,
  `percentage` DECIMAL(6,2) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  `status` INT NULL,
  PRIMARY KEY (`id`));

