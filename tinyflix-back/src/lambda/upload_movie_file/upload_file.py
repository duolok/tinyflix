import json
import boto3
import os
from utils import create_response
from s3_service import S3Service

def lambda_handler(event, context):
    bucket_name = os.environ.get('MOVIE_BUCKET')

    if not bucket_name:
        return create_response(500, 'S3 bucket name not configured in environment variables.')

    s3_service = S3Service(bucket_name)
    
    try:
        file_name = event['queryStringParameters']['file_name']
        file_type = event['queryStringParameters']['file_type']
    except KeyError:
        return create_response(400, 'Missing file_name or file_type in query parameters.')
    
    presigned_url = s3_service.generate_presigned_url(key=file_name, file_type=file_type)
    if presigned_url:
        return create_response(200, {'presigned_url': presigned_url})
    else:
        return create_response(500, 'Error generating presigned URL.')
