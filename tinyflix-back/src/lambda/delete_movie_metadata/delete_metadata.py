import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['MOVIE_TABLE'])

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        movie_name = body['movie_name']
        response = table.delete_item(Key={'name': movie_name})
        return create_response(200, json.dumps({'message': 'Metadata deleted successfully'}), cors=True)
    except Exception as e:
        print(f"Error: {str(e)}")
        return create_response(500, json.dumps({'error': str(e)}), cors=True)

def create_response(status_code, body, cors=True):
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

