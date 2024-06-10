import json
import os
from ..services.dynamodb_service import DynamoDbService
from ..services.s3_service import S3Service
from ..config import Config

dynamodb_service = DynamoDbService(config.movie_table)
s3_service = S3Service(config.movie_bucket)

def lambda_handler(event, context):
    payload = json.loads(event['body'])
    movie_id = payload['id']

    movie = dynamodb_service.get_movie_metadata(movie_id)
    if not movie:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Movie not found'})
        }

    destination_path = os.path.join('/tmp', f"{movie.id}.mp4")
    if s3_service.download_file(movie.s3_key, destination_path):
        with open(destination_path, 'rb') as f:
            content = f.read()
        return {
            'statusCode': 200,
            'body': content,
            'headers': {
                'Content-Type': 'video/mp4'
            },
            'isBase64Encoded': True
        }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to download file from S3'})
        }
