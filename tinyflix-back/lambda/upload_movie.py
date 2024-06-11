import json
import os
from ..models.movie import Movie
from ..services.dynamodb_service import DynamoDbService
from ..services.s3_service import S3Service

dynamodb_service = DynamoDbService(os.environ['MOVIE_TABLE'])
s3_service = S3Service(os.environ['MOVIE_BUCKET'])

def lambda_handler(event, context):
    payload = json.loads(event['body'])
    movie_id = payload['id']
    file_path = os.path.join('/tmp', f"{payload['file_name']}")
    
    if not os.path.exists(file_path):
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'File not found'})
        }

    s3_key = f"movies/{movie_id}.mp4"
    upload_successful, file_metadata = s3_service.upload_file(s3_key, file_path)

    if upload_successful:
        movie = Movie(
            id=movie_id,
            title=payload['title'],
            genre=payload['genre'],
            director=payload['director'],
            actors=payload['actors'],
            rating=payload.get('rating'),
            s3_key=s3_key,
            file_name=file_metadata['file_name'],
            file_type=file_metadata['file_type'],
            file_size=file_metadata['file_size'],
            creation_time=file_metadata['creation_time'],
            last_modified_time=file_metadata['last_modified_time'],
            description=payload.get('description')
        )
        dynamodb_service.save_movie_metadata(movie)
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'success'})
        }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to upload file to S3'})
        }

