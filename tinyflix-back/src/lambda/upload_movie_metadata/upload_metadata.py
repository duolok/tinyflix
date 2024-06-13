from uuid import uuid1
import json
import boto3
import os
from utils import create_response

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['MOVIE_TABLE'])

def lambda_handler(event, context):
    try:
        body = event['body']
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
        
        if 'name' not in data:
            return create_response(400, json.dumps({'error': 'Missing required key: name'}))
        if 'id' not in data:
            data['name'] = str(uuid1()) + data['name']

        table.put_item(Item=data)
        return create_response(200, json.dumps({'message': 'Movie metadata uploaded successfully', 'data': data}))
    except Exception as e:
        return create_response(500, json.dumps({'error': str(e)}))
