from uuid import uuid1
import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['MOVIE_TABLE'])

def lambda_handler(event, context):
    try:
        print("Received event: ", json.dumps(event, indent=2))
        
        if 'body' not in event:
            raise ValueError("Missing 'body' in event")
        
        body = json.loads(event['body'])
        print("Parsed body: ", body)
        
        metadata = {
            'id': body['title'] + '#' + str(uuid1()),
            'name': body['title'],  
            'title': body['title'],
            'description': body['description'],
            'actors': body['actors'],  
            'directors': body['directors'],  
            'genres': '|'.join(body['genres']) if isinstance(body['genres'], list) else body['genres'],
            'movieFilePath': body['movieFilePath'],
            'imageFilePath': body['imageFilePath'],
            'movieFileType': body['movieType'],
            'movieFileSize': str(body['movieSize']),
            'movieFileCreationTime': body['movieCreationTime'],
            'movieFileLastModified': body['movieLastModified'],
            'imageFileType': body['imageType'],
            'imageFileSize': str(body['imageSize']),
            'imageFileCreationTime': body['imageCreationTime'],
            'imageFileLastModified': body['imageLastModified'],
        }

        table.put_item(Item=metadata)
        return create_response(200, json.dumps({'message': 'Movie metadata uploaded successfully'}), cors=True)
    except json.JSONDecodeError as e:
        print("JSON decode error: ", str(e))
        return create_response(400, json.dumps({'error': 'Invalid JSON format'}), cors=True)
    except Exception as e:
        print("Exception: ", str(e))
        return create_response(500, json.dumps({'error': str(e)}), cors=True)
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

