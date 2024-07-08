import json
import boto3
import os

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        title = body['title']
        files = body['files']
        bucket_name = os.environ['MOVIE_BUCKET']
        upload_urls = []

        for file_name in files:
            base_name, ext = os.path.splitext(file_name)
            original_file_name = f"{base_name}_original{ext}"
            key = f'movies/{title}/{original_file_name}'
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={'Bucket': bucket_name, 'Key': key},
                ExpiresIn=3600
            )
            upload_urls.append(presigned_url)

        return create_response(200, json.dumps({'upload_urls': upload_urls}), cors=True)
    except Exception as e:
        return create_response(500, json.dumps({'error': str(e)}), cors=True)

def create_response(status_code, body, cors=False):
    response = {
        'statusCode': status_code,
        'body': body,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Methods': '*',
        }
    }
    return response

