import json
import boto3
import os
from utils import create_response
from s3_service import S3Service

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        file_name = body['file_name']
        bucket_name = os.environ['BUCKET_NAME']
        
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': bucket_name, 'Key': file_name},
            ExpiresIn=3600  # URL expiration time in seconds
        )
        
        return create_response(200, json.dumps({'upload_url': presigned_url}))
    except Exception as e:
        return create_response(500, json.dumps({'error': str(e)}))
