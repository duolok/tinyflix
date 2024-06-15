import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    bucket_name = 'serverless-movie-bucket'
    file_key = event['file_key']

    try:
        presigned_url = s3_client.generate_presigned_url('get_object',
                                                         Params={'Bucket': bucket_name, 'Key': file_key},
                                                         ExpiresIn=3600)  
        return {
            'statusCode': 200,
            'body': json.dumps({'presigned_url': presigned_url})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
