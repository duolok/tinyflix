import json
import boto3
import os

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        movie_path = body['moviePath']
        bucket_name = os.environ['MOVIE_BUCKET']
        folder_name = '/'.join(movie_path.split('/')[:-1]) + '/'
        
        objects_to_delete = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
        if 'Contents' in objects_to_delete:
            delete_objects = [{'Key': obj['Key']} for obj in objects_to_delete['Contents']]
            response = s3_client.delete_objects(
                Bucket=bucket_name,
                Delete={'Objects': delete_objects}
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return create_response(200, json.dumps({'message': 'Folder and its contents deleted successfully.'}))
            else:
                return create_response(500, json.dumps({'error': 'Failed to delete folder and its contents.'}))
        else:
            return create_response(404, json.dumps({'error': 'Folder not found.'}))
    except Exception as e:
        return create_response(500, json.dumps({'error': str(e)}))

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
