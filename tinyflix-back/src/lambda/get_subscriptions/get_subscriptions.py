import json
import os
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['SUBSCRIPTIONS_TABLE'])

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        email = body.get('userId')

        if not email:
            return create_response(400, json.dumps({'error': 'Email is not provided.'}), cors=True)

        response = table.get_item(
            Key={
                'userId': email
            }
        )

        if 'Item' not in response:
            return create_response(404, json.dumps({'error': 'User not found.'}), cors=True)

        items = response['Item']
        body = {'data': json.loads(json.dumps(items, default=decimal_default))}
        return create_response(200, json.dumps(body), cors=True)
    except Exception as e:
        return create_response(500, json.dumps({'error': str(e)}), cors=True)

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def create_response(status_code, body, cors=False):
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

