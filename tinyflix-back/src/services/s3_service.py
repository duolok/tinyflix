import boto3
from botocore.exceptions import NoCredentialsError
from builtins import FileNotFoundError

class S3Service:
    def __init__(self, bucket_name):
        self.client = boto3.client('s3')
        self.bucket_name = bucket_name

    def create_bucket(self):
        self.client.create_bucket(Bucket=self.bucket_name)

    def upload_file(self, key, file_path):
        try:
            self.client.upload_file(file_path, self.bucket_name, key)
            response = self.client.head_object(Bucket=self.bucket_name, Key=key)
            file_metadata = {
                'file_name': key.split('/')[-1],
                'file_type': response['ContentType'],
                'file_size': response['ContentLength'],
                'creation_time': response['LastModified'].isoformat(),
                'last_modified_time': response['LastModified'].isoformat()
            }
            return True, file_metadata
        except FileNotFoundError:
            print("The file was not found.")
        except NoCredentialsError:
            print("Credentials not available.")
        return False, None

    def generate_presigned_url(self, key, file_type, expiration=3600):
        try:
            presigned_url = self.client.generate_presigned_url(
                'put_object',
                Params={'Bucket': self.bucket_name, 'Key': key, 'ContentType': file_type},
                ExpiresIn=expiration
            )
            return presigned_url
        except NoCredentialsError:
            print("Credentials not available.")
            return None

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

    def print_all_buckets(self):
        [print(f"\t{bucket['Name']}") for bucket in self.client.list_buckets()['Buckets']]

    def print_all_objects(self):
        print("=== All objects in a bucket ===\n" +
            "\n".join([f"\t{o['Key']}" for o in self.client.list_objects(Bucket=self.bucket_name)['Contents']]))

