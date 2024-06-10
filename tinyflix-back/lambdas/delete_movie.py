import json
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

    if s3_service.delete_file(movie.s3_key):
        dynamodb_service.delete_movie_metadata(movie_id)
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'success'})
        }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to delete file from S3'})
        }
