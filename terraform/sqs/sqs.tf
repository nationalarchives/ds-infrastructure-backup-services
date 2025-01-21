resource "aws_sqs_queue" "backup_check_in_queue" {
    name                      = "backup-check-in-queue.fifo"
    fifo_queue                = true
    deduplication_scope       = "messageGroup"
    fifo_throughput_limit     = "perMessageGroupId"
    sqs_managed_sse_enabled   = true
    receive_wait_time_seconds = 20
    redrive_policy = jsonencode({
        deadLetterTargetArn = aws_sqs_queue.backup_check_in_dl_queue.arn
        maxReceiveCount     = 1
    })
    message_retention_seconds = 86400
}

resource "aws_sqs_queue" "backup_check_in_dl_queue" {
    name                      = "backup-check-in-dl-queue.fifo"
    message_retention_seconds = 345600
    fifo_queue                = true
    sqs_managed_sse_enabled   = true
    receive_wait_time_seconds = 20
}

resource "aws_sqs_queue" "backup_compressor_queue" {
    name                      = "backup-compressor-queue.fifo"
    fifo_queue                = true
    deduplication_scope       = "messageGroup"
    fifo_throughput_limit     = "perMessageGroupId"
    sqs_managed_sse_enabled   = true
    receive_wait_time_seconds = 20
    redrive_policy = jsonencode({
        deadLetterTargetArn = aws_sqs_queue.backup_compressor_dl_queue.arn
        maxReceiveCount     = 1
    })
    message_retention_seconds = 86400
}

resource "aws_sqs_queue" "backup_compressor_dl_queue" {
    name                      = "backup-compressor-dl-queue.fifo"
    message_retention_seconds = 345600
    fifo_queue                = true
    sqs_managed_sse_enabled   = true
    receive_wait_time_seconds = 20
}

output "backup_check_in_queue_url" {
    value = aws_sqs_queue.backup_check_in_queue.url
}

output "backup_check_in_queue_arn" {
    value = aws_sqs_queue.backup_check_in_queue.arn
}

output "backup_compressor_queue_url" {
    value = aws_sqs_queue.backup_compressor_queue.url
}

output "backup_compressor_queue_arn" {
    value = aws_sqs_queue.backup_compressor_queue.arn
}
