# python version for klayers need updating when the python version for lambda changes

# build layer for lambda - can be used to combine different libraries
# 1. create directory python
# 2. pip install -t python pytz
# 3. zip -r pytz_layer_2023.2.zip python
# 4. copy zip to s3 bucket

##
# python 3.12
# ------------------------------------------------------------------------------
# compatible runtimes python3.9, python3.10, python3.11 and python3.12
data "klayers_package_latest_version" "boto3-3_12" {
    name   = "boto3"
    region = "eu-west-2"

    python_version = "3.12"
}

# compatible runtimes python3.9, python3.10, python3.11 and python3.12
data "klayers_package_latest_version" "mysql-connector-python-3_12" {
    name   = "mysql-connector-python"
    region = "eu-west-2"

    python_version = "3.12"
}

resource "aws_lambda_layer_version" "pytz_2024_2" {
    layer_name = "pytz_2024_2"

    s3_bucket = "tna-backup-tooling"
    s3_key    = "lambda/layers/pytz_layer_2024.2.zip"

    compatible_runtimes = [
        "python3.9",
        "python3.10",
        "python3.11",
        "python3.12",
    ]
}

resource "aws_lambda_layer_version" "datetime_5_5" {
    layer_name = "datetime_5_5"

    s3_bucket = "tna-backup-tooling"
    s3_key    = "lambda/layers/DateTime-5.5.zip"

    compatible_runtimes = [
        "python3.9",
        "python3.10",
        "python3.11",
        "python3.12",
    ]
}
