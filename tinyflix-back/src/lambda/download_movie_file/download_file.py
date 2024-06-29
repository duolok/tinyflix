import json
import boto3
from urllib.parse import unquote_plus
import os

bucket_name = os.environ['MOVIE_BUCKET']

def lambda_handler(event, context):
    if event['httpMethod'] == 'OPTIONS':
        return create_response(200, '', cors=True)
    
    s3_client = boto3.client('s3')
    file_key = unquote_plus(event['queryStringParameters']['file_key'])

    try:
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_key},
            ExpiresIn=3600)
        return create_response(200, json.dumps({'presigned_url': presigned_url}), cors=True)
    except Exception as e:
        return create_response(500, json.dumps({'error': str(e)}), cors=True)

def create_response(status_code, body, cors=False):
    response = {
        'statusCode': status_code,
        'body': body,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT,DELETE',
        }
    }
    return response

