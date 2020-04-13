import boto3
import os


class S3FileManager:

    def __init__(self):
        if os.getenv('ENVIRONMENT') == 'prod':
            self.s3_client = boto3.client('s3')
        else:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')

    def upload_file(self, file_name, object_name=None):

        if object_name is None:
            object_name = file_name

        self.s3_client.upload_file(file_name, self.bucket_name, object_name)

    def download_file(self, object_name, file_name):
        with open(file_name, 'wb') as f:
            self.s3_client.download_fileobj(self.bucket_name, object_name, f)

    def list_object_keys(self, directory=''):
        response = self.s3_client.list_objects(
            Bucket=self.bucket_name
        )

        return [s3_object['Key'] for s3_object in response['Contents'] if s3_object['Key'].startswith(directory) and s3_object['Key'] != directory]

    def move_object(self, source, target):
        self.s3_client.copy({
            'Bucket': self.bucket_name,
            'Key': source
        }, self.bucket_name, target)
        self.s3_client.delete_object(
            Bucket=self.bucket_name,
            Key=source,
        )

    def file_exists(self, object_key):
        try:
            self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=object_key,
            )
        except self.s3_client.exceptions.NoSuchKey:
            return False

        return True