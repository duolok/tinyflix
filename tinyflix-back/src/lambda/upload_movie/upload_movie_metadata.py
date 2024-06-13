import json
import boto3
import os
from utility.utils import create_response

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['MOVIE_TABLE'])

def lambda_handler(event, context):
    data = json.loads(event['body'])
    table.put_item(Item=data)
    body = {'body': json.dumps({'message': 'Movie metadata uploaded successfully'})}
    return  create_response(200, body)
