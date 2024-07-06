import boto3
import json
import os
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['MOVIE_TABLE'])

def lambda_handler(event, context):
    search_term = event.get('queryStringParameters', {}).get('searchQuery')
    index_names = ['TitleIndex', 'DescptIndex', 'ActorsIndex', 'DirectorsIndex', 'GenresIndex']

    results = []
    for index in index_names:
        response = query_index(index, search_term)
        if 'Items' in response:
            results.extend(response['Items'])

    unique_results = {item['id']: item for item in results}.values()
    body = {'data': list(unique_results), 'search_term': search_term}

    return create_response(200, body, cors=True)

def query_index(index_name, search_term):
    try:
        response = table.query(
            IndexName=index_name,
            KeyConditionExpression=Key(index_name.split('Index')[0].lower()).eq(search_term)
        )
        return response
    except Exception as e:
        print(f"Error querying index {index_name}: {str(e)}")
        return {}

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def create_response(status_code, body, cors=False):
    response = {
        'statusCode': status_code,
        'body': json.dumps(body, cls=DecimalEncoder),
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

