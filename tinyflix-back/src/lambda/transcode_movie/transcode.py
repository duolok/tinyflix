import boto3
import os
import json
import logging
import mimetypes
import subprocess
import urllib.parse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
bucket_name = os.environ['MOVIE_BUCKET']

def lambda_handler(event, context):
    try:
        output_keys = []
        os.system("chmod +x /opt/bin/ffmpeg")

        record = event['Records'][0]
        key = record['s3']['object']['key']
        decoded_key = urllib.parse.unquote_plus(key)
        logger.info(f"Processing file: {decoded_key}")
        download_path = f'/tmp/{os.path.basename(decoded_key)}'

        # Skip files without "_original" in their names
        if "_original" not in decoded_key:
            logger.info(f"Skipping file {decoded_key} as it does not have '_original' in its name.")
            return create_response(200, json.dumps({'message': 'Skipped non-original file'}), cors=True)

        try:
            s3_client.head_object(Bucket=bucket_name, Key=decoded_key)
            s3_client.download_file(bucket_name, decoded_key, download_path)
            logger.info(f"Downloaded file to: {download_path}")

        except s3_client.exceptions.NoSuchKey as e:
            logger.error(f"File not found in S3 bucket: {bucket_name}/{decoded_key}. Error: {e}")
            return create_response(404, json.dumps({'error': 'File not found'}), cors=True)

        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                logger.error(f"File not found: {bucket_name}/{decoded_key}. Error: {e}")
                return create_response(404, json.dumps({'error': 'File not found'}), cors=True)
            else:
                logger.error(f"ClientError: {e}")
                return create_response(500, json.dumps({'error': 'ClientError'}), cors=True)

        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return create_response(500, json.dumps({'error': 'Error downloading file'}), cors=True)

        if is_video_file(download_path):
            resolutions = {
                '360p': '640x360',
                '480p': '640x480',
                '720p': '1280x720',
            }

            base_name, ext = os.path.splitext(os.path.basename(decoded_key))
            base_name = base_name.replace('_original', '')
            directory = os.path.dirname(decoded_key)

            for res, size in resolutions.items():
                output_key = f"{directory}/{base_name}_{res}{ext}"
                output_path = f"/tmp/{base_name}_{res}{ext}"
                logger.info(f"Transcoding to resolution: {res}")
                error_message = transcode_video(download_path, output_path, size)
                if error_message:
                    logger.error(f"Error transcoding video: {error_message}")
                    continue
                logger.info(f"Transcoded file path: {output_path}")
                try:
                    s3_client.upload_file(output_path, bucket_name, output_key)
                    logger.info(f"Uploaded file to: {output_key}")
                    output_keys.append(output_key)
                except Exception as e:
                    logger.error(f"Error uploading file: {e}")
                finally:
                    if os.path.exists(output_path):
                        os.remove(output_path)
        else:
            logger.info(f"Skipping non-video file: {decoded_key}")

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
    cmd = [
        ffmpeg_path, '-i', input_file, '-vf', f'scale={scale}', output_file
    ]
    
    logger.info(f"Running command: {' '.join(cmd)}")
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if process.returncode != 0:
        logger.error(f"FFmpeg error: {process.stderr.decode('utf-8')}")
        return process.stderr.decode('utf-8')
    else:
        logger.info("Transcoding successful")
        return None

