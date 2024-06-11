import json
import boto3
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        data = json.loads(event['body'])
        bucket = os.environ['MOVIE_BUCKET']
        file_name = data['file_name']
        
        presigned_url = s3.generate_presigned_url(
            'put_object',
            Params={'Bucket': bucket, 'Key': file_name, 'ContentType': 'video/mp4'},
            ExpiresIn=3600
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'presigned_url': presigned_url})
        }
    except Exception as e:
        print("Error: ", e)
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)})
        }

