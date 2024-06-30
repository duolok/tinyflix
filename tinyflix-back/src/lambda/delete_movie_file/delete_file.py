import json
import boto3
import os

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        movie_path = body['url']
        bucket_name = os.environ['MOVIE_BUCKET']
        
        objects_to_delete = s3_client.list_objects(Bucket=bucket_name, Prefix=movie_path)
        delete_keys = {'Objects': []}
        delete_keys['Objects'] = [{'Key': obj['Key']} for obj in objects_to_delete.get('Contents', [])]
        if delete_keys['Objects']:
            s3_client.delete_objects(Bucket=bucket_name, Delete=delete_keys)

        return create_response(200, json.dumps({'message': 'Movie file deleted successfully.'}), cors=True)
    except Exception as e:
        print(f"Error: {str(e)}")
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
    if cors:
        response['headers']['Access-Control-Allow-Origin'] = '*'
    return response

