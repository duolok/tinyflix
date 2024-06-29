import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['MOVIE_TABLE'])

def lambda_handler(event, context):
    try:
        movie_id = event['pathParameters']['id']
        response = table.delete_item(
            Key={
                'id': movie_id
            }
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return create_response(200, json.dumps({'message': 'Movie metadata deleted successfully.'}))
        else:
            return create_response(500, json.dumps({'error': 'Failed to delete movie metadata.'}))
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


