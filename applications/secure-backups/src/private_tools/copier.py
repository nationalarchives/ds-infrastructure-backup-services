import boto3
from boto3.s3.transfer import TransferConfig

class TransferBox:

    def __init__(self, use_threads: bool=True, max_concurrency: int=10, multipart_threshold: int=107374182400):
        self.use_threads = use_threads
        self.max_concurrency = max_concurrency
        self.multipart_threshold = multipart_threshold
        self.upload_config = TransferConfig(multipart_threshold = self.multipart_threshold,
                                            max_concurrency = self.max_concurrency,
                                            use_threads = self.use_threads)

    def upload(self, filename, bucket, key, extra_args=None, callback=None):
        s3 = boto3.client('s3')
        s3.upload_file(Filename=filename, Bucket=bucket, Key=key, ExtraArgs=extra_args, Callback=callback)
