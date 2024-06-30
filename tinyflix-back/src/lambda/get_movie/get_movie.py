import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['MOVIE_TABLE'])

def lambda_handler(event, context):
    body = json.loads(event['body'])
    movie_name = body.get('name')
    if not movie_name:
        return create_response(400, json.dumps({'error': 'Movie name is required'}), cors=True)

    try:
        response = table.get_item(
            Key={
                'name': movie_name
            }
        )
    except Exception as e: 
        return create_response(500, json.dumps({'error': str(e)}), cors=True)

    if 'Item' not in response:
        return create_response(404, json.dumps({'error': 'Movie not found'}), cors=True)
    
    body = { 'data': response['Item'] }
    return create_response(200, json.dumps(body, default=str), cors=True)

def create_response(status_code, body, cors=True):
    response = {
        'statusCode': status_code,
        'body': body,
        'headers': {
            'Content-Type': 'application/json',
        }
    }
    if cors:
        response['headers']['Access-Control-Allow-Origin'] = '*'
        response['headers']['Access-Control-Allow-Headers'] = '*'
        response['headers']['Access-Control-Allow-Methods'] = '*'
    return response

