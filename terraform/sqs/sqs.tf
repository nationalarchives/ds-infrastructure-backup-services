resource "aws_sqs_queue" "backup_check_in_queue" {
    name                    = "backup-check-in-queue.fifo"
    fifo_queue              = true
    deduplication_scope     = "messageGroup"
    fifo_throughput_limit   = "perMessageGroupId"
    sqs_managed_sse_enabled = true
}

output "backup_check_in_queue_url" {
    value = aws_sqs_queue.backup_check_in_queue.url
}
