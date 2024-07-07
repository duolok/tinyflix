import json
import os
import boto3
import logging
from decimal import Decimal

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TOP_MOVIES_TABLE'])

def lambda_handler(event, context):
    user_id = event['queryStringParameters']['userId']
    
    try:
        logger.info("Querying for userId: %s", user_id)
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('userId').eq(user_id)
        )
        items = response.get('Items', [])
        logger.info("Items retrieved: %s", items)
        
        movies = []

        for item in items:
            logger.info("Processing item: %s", item)
            #for movie_item in item['movies']['L']:
            #    logger.info("Processing movie item: %s", movie_item)
            #    movie_data = movie_item['M']['movie']['M']
            #    score = movie_item['M']['score']['N']
            #    
            #    parsed_movie_data = {key: parse_dynamodb_item(value) for key, value in movie_data.items()}
            #    parsed_movie_data['score'] = float(score)
            #    
            #    logger.info("Parsed movie data: %s", parsed_movie_data)
            movies.append(item)

        body = { 'data': movies }
        return create_response(200, json.dumps(body, default=decimal_default))
    except Exception as e:
        logger.error("Error: %s", e)
        return create_response(500, json.dumps({'error': str(e)}))

def parse_dynamodb_item(item):
    if isinstance(item, dict):
        if 'S' in item:
            return item['S']
        elif 'N' in item:
            return float(item['N']) if '.' in item['N'] else int(item['N'])
        elif 'M' in item:
            return {k: parse_dynamodb_item(v) for k, v in item['M'].items()}
        elif 'L' in item:
            return [parse_dynamodb_item(i) for i in item['L']]
    return item

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
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Methods': '*',
        }
    }
    if cors:
        response['headers']['Access-Control-Allow-Origin'] = '*'
    return response
