import boto3
from botocore.exceptions import NoCredentialsError, FileNotFoundError

class S3Service:
    def __init__(self, bucket_name):
        self.client = boto3.client('s3')
        self.bucket_name = bucket_name

    def upload_file(self, key, file_path):
        try:
            self.client.upload_file(file_path, self.bucket_name, key)
            return True
        except FileNotFoundError:
            print("The file was not found.")
        except NoCredentialsError:
            print("Credentials not available.")
        return False

    def download_file(self, key, destination_path):
        try:
            self.client.download_file(self.bucket_name, key, destination_path)
            return True
        except NoCredentialsError:
            print("Credentials not available.")
        return False

    def delete_file(self, key):
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except NoCredentialsError:
            print("Credentials not available.")
        return False

