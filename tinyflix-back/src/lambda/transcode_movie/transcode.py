import boto3
import os
import json
import logging
import mimetypes

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
bucket_name = os.environ['MOVIE_BUCKET']

def lambda_handler(event, context):
    try:
        output_keys = []
        os.system("chmod +x /opt/bin/ffmpeg")
        for record in event['Records']:
            key = record['s3']['object']['key']
            logger.info(f"Processing file: {key}")
            download_path = f'/tmp/{os.path.basename(key)}'
            logger.info(f"KEY => {key} ")
            logger.info(f"KEY BASENAME {os.path.basename(key)} ")
            logger.info(f"BUCKET NAME {bucket_name} ")
            logger.info(f"DONLOAD PATH {download_path} ")
            s3_client.download_file(bucket_name, key, download_path)
            logger.info(f"Downloaded file to: {download_path}")

            if is_video_file(download_path):
                resolutions = {
                    '480p': '640:480',
                    '720p': '1280:720',
                    '1080p': '1920:1080'
                }

                base_name, ext = os.path.splitext(key)
                directory = os.path.dirname(key)

                for res, size in resolutions.items():
                    output_key = f"{directory}/{os.path.basename(base_name)}_{res}{ext}"
                    output_path = f"/tmp/{os.path.basename(base_name)}_{res}{ext}"
                    logger.info(f"Transcoding to resolution: {res}")
                    error_message = transcode_video(download_path, output_path, size)
                    if error_message:
                        logger.error(f"Error transcoding video: {error_message}")
                        continue
                    logger.info(f"Transcoded file path: {output_path}")
                    s3_client.upload_file(output_path, bucket_name, output_key)
                    logger.info(f"Uploaded file to: {output_key}")
                    output_keys.append(output_key)
            else:
                logger.info(f"Skipping non-video file: {key}")
                output_keys.append(key)

        body = {
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
        }
    }
    if cors:
        response['headers']['Access-Control-Allow-Origin'] = '*'
        response['headers']['Access-Control-Allow-Headers'] = '*'
        response['headers']['Access-Control-Allow-Methods'] = '*'
    return response

def is_video_file(file_path):
    video_extensions = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"}
    ext = os.path.splitext(file_path)[1].lower()
    if ext in video_extensions:
        return True
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type and mime_type.startswith("video")

def transcode_video(input_file, output_file, scale):
    if not is_video_file(input_file):
        logger.info(f"Skipping non-video file: {input_file}")
        return "Not a video file"
    
    ffmpeg_path = "/opt/bin/ffmpeg"  
    cmd = f"{ffmpeg_path} -i {input_file} -vf scale={scale} {output_file}"
    logger.info(f"Running command: {cmd}")

    exit_code = os.system(cmd)

    if exit_code != 0:
        logger.error(f"FFmpeg error: Command exited with status {exit_code}")
        return f"Command exited with status {exit_code}"
    else:
        logger.info("Transcoding successful")
        return None

