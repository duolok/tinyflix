import json
import boto3
import os
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['MOVIE_TABLE'])

def lambda_handler(event, context):
    try:
        print("Received event: ", json.dumps(event, indent=2))

        if 'body' not in event:
            raise ValueError("Missing 'body' in event")

        body = json.loads(event['body'])
        print("Parsed body: ", body)

        if 'object' not in body:
            raise ValueError("Missing 'object' in body")

        movie_data = body['object']
        
        if 'name' not in movie_data:
            raise ValueError("Missing 'name' in movie data")
        
        movie_name = movie_data['name']
        movie_metadata = get_existing_movie_metadata(movie_name)
        
        updated_metadata = {
            'title': movie_data['title'],
            'description': movie_data['description'],
            'releaseDate': movie_data['releaseDate'],
            'duration': movie_data['duration'],
            'actors': '|'.join(movie_data['actors']) if isinstance(movie_data['actors'], list) else movie_data['actors'],
            'directors': '|'.join(movie_data['directors']) if isinstance(movie_data['directors'], list) else movie_data['directors'],
            'genres': '|'.join(movie_data['genres']) if isinstance(movie_data['genres'], list) else movie_data['genres'],
            'movieFilePath': movie_data.get('movieFilePath', movie_metadata.get('movieFilePath')),
            'imageFilePath': movie_data.get('imageFilePath', movie_metadata.get('imageFilePath')),
            'movieFileType': movie_data.get('movieFileType', movie_metadata.get('movieFileType', '')),
            'movieFileSize': movie_data.get('movieFileSize', movie_metadata.get('movieFileSize', '')),
            'movieFileCreationTime': movie_data.get('movieFileCreationTime', movie_metadata.get('movieFileCreationTime', '')),
            'movieFileLastModified': movie_data.get('movieFileLastModified', movie_metadata.get('movieFileLastModified', '')),
            'imageFileType': movie_data.get('imageFileType', movie_metadata.get('imageFileType', '')),
            'imageFileSize': movie_data.get('imageFileSize', movie_metadata.get('imageFileSize', '')),
            'imageFileCreationTime': movie_data.get('imageFileCreationTime', movie_metadata.get('imageFileCreationTime', '')),
            'imageFileLastModified': movie_data.get('imageFileLastModified', movie_metadata.get('imageFileLastModified', '')),
        }

        update_expression = "SET " + ", ".join(f"#{key} = :{key}" for key in updated_metadata.keys())
        expression_attribute_names = {f"#{key}": key for key in updated_metadata.keys()}
        expression_attribute_values = {f":{key}": value for key, value in updated_metadata.items()}

        table.update_item(
            Key={'name': movie_name},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )

        return create_response(200, json.dumps({'message': 'Movie metadata updated successfully'}), cors=True)
    except ClientError as e:
        print("Client error: ", str(e))
        return create_response(500, json.dumps({'error': f"ClientError: {str(e)}"}), cors=True)
    except json.JSONDecodeError as e:
        print("JSON decode error: ", str(e))
        return create_response(400, json.dumps({'error': f"JSONDecodeError: {str(e)}"}), cors=True)
    except ValueError as e:
        print("Value error: ", str(e))
        return create_response(400, json.dumps({'error': f"ValueError: {str(e)}"}), cors=True)
    except Exception as e:
        print("Exception: ", str(e))
        return create_response(500, json.dumps({'error': f"Exception: {str(e)}"}), cors=True)

def get_existing_movie_metadata(movie_name):
    response = table.get_item(Key={'name': movie_name})
    if 'Item' not in response:
        raise ValueError(f"Movie with name {movie_name} not found")
    return response['Item']

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
