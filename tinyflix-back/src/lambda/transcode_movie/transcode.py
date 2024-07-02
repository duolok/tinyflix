import boto3
import os
import ffmpeg
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
bucket_name = os.environ['MOVIE_BUCKET']

def lambda_handler(event, context):
    try:
        key = event['Records'][0]['s3']['object']['key']
        logger.info(f"Processing file: {key}")
        download_path = f'/tmp/{os.path.basename(key)}'
        s3_client.download_file(bucket_name, key, download_path)
        logger.info(f"Downloaded file to: {download_path}")

        resolutions = ['480p', '720p', '1080p']
        output_keys = []

        base_name, ext = os.path.splitext(key)
        directory = os.path.dirname(key)

        ffmpeg_executable = "/opt/bin/ffmpeg"  # Path to the ffmpeg binary

        for res in resolutions:
            output_key = f"{directory}/{os.path.basename(base_name)}_{res}{ext}"
            output_path = f"/tmp/{os.path.basename(base_name)}_{res}{ext}"
            logger.info(f"Transcoding to resolution: {res}")
            (
                ffmpeg
                .input(download_path)
                .output(output_path, s=f'video_{res}')
                .run(cmd=ffmpeg_executable)
            )
            logger.info(f"Transcoded file path: {output_path}")
            s3_client.upload_file(output_path, bucket_name, output_key)
            logger.info(f"Uploaded file to: {output_key}")
            output_keys.append(output_key)

        body = {
            'original_key': key,
            'output_keys': output_keys,
        }

        return create_response(200, json.dumps(body), cors=True)
    except Exception as e:
        logger.error(f"Error processing file: {e}")
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

