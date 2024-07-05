import json
import os
import boto3
import logging
from decimal import Decimal
from urllib.parse import unquote_plus

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['SUBSCRIPTIONS_TABLE'])

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    try:
        query_params = event.get('queryStringParameters', {})
        email = query_params.get('email') if query_params else None

        if email:
            # Decode email in case it's URL encoded
            email = unquote_plus(email)

        logger.info("Extracted email: %s", email)

        if not email:
            logger.error("Email is not provided in the request")
            return create_response(400, {'error': 'Email is not provided.'}, cors=True)

        response = table.get_item(
            Key={
                'userId': email
            }
        )
        logger.info("DynamoDB response: %s", json.dumps(response))

        if 'Item' not in response:
            logger.error("User not found for email: %s", email)
            return create_response(404, {'error': 'User not found.'}, cors=True)

        items = response['Item']
        body = {'data': json.loads(json.dumps(items, default=decimal_default))}
        logger.info("Returning body: %s", json.dumps(body))
        return create_response(200, body, cors=True)
    except Exception as e:
        logger.exception("Exception occurred while processing the request")
        return create_response(500, {'error': str(e)}, cors=True)

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def create_response(status_code, body, cors=False):
    response = {
        'statusCode': status_code,
        'body': json.dumps(body),
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

