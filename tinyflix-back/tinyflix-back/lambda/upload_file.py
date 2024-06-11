import json
import boto3
import os
from base64 import b64decode
from botocore.exceptions import NoCredentialsError

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        data = json.loads(event['body'])
        bucket = os.environ['MOVIE_BUCKET']
        file_name = data['file_name']
        
        file_content = b64decode(data['file_content'])
        s3.put_object(Bucket=bucket, Key=file_name, Body=file_content, ContentType='video/mp4')
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'File uploaded successfully'})
        }
    except NoCredentialsError:
        return {
            'statusCode': 403,
            'body': json.dumps({'message': 'Credentials not available'})
        }
    except Exception as e:
        print("Error: ", e)
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)})
        }

