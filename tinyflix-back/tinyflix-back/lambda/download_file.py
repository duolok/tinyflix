import json
import boto3
import os
from botocore.exceptions import NoCredentialsError

s3 = boto3.client('s3')

def lambda_handler(event, context):
    data = json.loads(event['body'])
    bucket = os.environ['MOVIE_BUCKET']
    file_name = data['file_name']

    try:
        response = s3.get_object(Bucket=bucket, Key=file_name)
        file_content = response['Body'].read().decode('base64')
        return {
            'statusCode': 200,
            'body': json.dumps({'file_content': file_content}),
            'isBase64Encoded': True,
            'headers': {
                'Content-Type': 'video/mp4'
            }
        }
    except NoCredentialsError:
        return {
            'statusCode': 403,
            'body': json.dumps({'message': 'Credentials not available'})
        }
    except s3.exceptions.NoSuchKey:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'File not found'})
        }

