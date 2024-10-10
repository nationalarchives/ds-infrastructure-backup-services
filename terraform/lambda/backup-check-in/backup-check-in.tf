data "archive_file" "lambda_backup_check_in" {
    type        = "zip"
    source_dir  = "${path.root}/lambda/backup-check-in/src"
    output_path = "${path.root}/lambda/backup-check-in-zip"
}

# allow Lambda to get object from S3 and write to CloudWatch logs
#
resource "aws_iam_policy" "lambda_s3_cw" {
    name = "lambda-backup-check-in"
    policy = templatefile("${path.module}/templates/lambda_s3_cw.json", {
        aws_account_id = var.aws_account_id
        region         = var.region
    })
}

resource "aws_iam_role" "lambda_execution_role" {
    name = "lambda-backup-check-in-execution-role"
    assume_role_policy = file("${path.root}/templates/assume-role-lambda-policy.json")

    managed_policy_arns = [
        "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
        aws_iam_policy.lambda_s3_cw.arn,
    ]

    description = "allow lambda to assume role and access s3 and cw"

    tags = var.tags
}

# using this option allows setting of log retention and removal of the log group
# when the function is destroyed
resource "aws_cloudwatch_log_group" "lambda_backup_check_in" {
    name              = "/aws/lambda/${aws_lambda_function.backup_check_in.function_name}"
    retention_in_days = 90
}

resource "aws_lambda_function" "backup_check_in" {
    filename         = data.archive_file.lambda_backup_check_in.output_path
    source_code_hash = data.archive_file.lambda_backup_check_in.output_base64sha256

    function_name = "backup_check_in"
    role          = aws_iam_role.lambda_execution_role.arn

    runtime = var.runtime
    layers  = var.layers

    handler = "backup-check-in.lambda_handler"

    memory_size = 512
    timeout     = 10

    ephemeral_storage {
        size = 512
    }

    vpc_config {
        subnet_ids = var.subnet_ids
        security_group_ids = concat(var.security_group_ids, [
            aws_security_group.lambda_backup_drop_zone_sg.id
        ])
    }

    environment {
        variables = {
            QUEUE_URL = "bar"
            ASM_ID = ""
        }
    }

    tags = merge(var.tags, {
        Role            = "backup check-in"
        ApplicationType = "python"
        CreatedBy       = "devops@nationalarchives.gov.uk"
        Service         = "backup"
        Name            = "backup_check_in"
    })
}

resource "aws_lambda_permission" "backup_check_in" {
    statement_id  = "AllowExecutionFromS3Bucket"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.backup_check_in.arn
    principal     = "s3.amazonaws.com"
    source_arn    = var.bucket_arn
}

resource "aws_s3_bucket_notification" "lambda_backup_check_in" {
    bucket = "${var.bucket_name}"

    lambda_function {
        events = [
            "s3:ObjectCreated:*"
        ]
        lambda_function_arn = "${aws_lambda_function.backup_check_in.arn}"
    }

    depends_on = [
        aws_lambda_permission.backup_check_in
    ]
}
