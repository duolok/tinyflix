import os
import json
import boto3
import logging
from botocore.exceptions import ClientError

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize the DynamoDB and SNS resources/clients
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# Retrieve environment variables
subscriptions_table = dynamodb.Table(os.environ['SUBSCRIPTIONS_TABLE'])
movies_table = dynamodb.Table(os.environ['MOVIE_TABLE'])
notification_topic_arn = os.environ['NOTIFICATION_TOPIC_ARN']

def lambda_handler(event, context):
    try:
        logger.info("Received event: %s", json.dumps(event, indent=2))

        movie = event['Records'][0]['dynamodb']['NewImage']
        movie_id = movie['name']['S']
        title = movie['title']['S']
        actors = movie['actors']['S'].split("|")
        genres = movie['genres']['S'].split("|")
        directors = movie['directors']['S'].split("|")

        logger.info(f"MOVIE : {movie}")
        logger.info(f"MOVIE_ID : {movie_id}")
        logger.info(f"ACTORS : {actors}")
        logger.info(f"TITLE : {title}")
        logger.info(f"GENRESS : {genres}")
        logger.info(f"DIRECTORS : {directors}")

        logger.info(f"Processing movie: {movie_id}, title: {title}")

        response = subscriptions_table.scan()
        users_to_notify = []

        for item in response['Items']:
            user_id = item['userId']
            subscriptions = item['subscriptions']
            
            if (
                set(subscriptions.get('actors', [])) & set(actors) or
                set(subscriptions.get('genres', [])) & set(genres) or
                set(subscriptions.get('directors', [])) & set(directors)
            ):
                users_to_notify.append(user_id)

        logger.info(f"Users to notify: {users_to_notify}")

        # Send notifications to the matched users
        for user_id in users_to_notify:
            send_notification(user_id, title)

        return create_response(200, json.dumps('Notifications sent successfully!'), cors=True)

    except ClientError as e:
        logger.error(f"Client error: {e.response['Error']['Message']}")
        return create_response(500, json.dumps('Error processing movie upload: ' + e.response['Error']['Message']), cors=True)
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        return create_response(500, json.dumps('Error: ' + str(e)), cors=True)

def send_notification(user_id, movie_title):
    try:
        sns.publish(
            TopicArn=notification_topic_arn,
            Subject='New Movie Uploaded',
            Message=f'A new movie "{movie_title}" matching your subscription criteria has been uploaded.',
            MessageAttributes={
                'userId': {
                    'DataType': 'String',
                    'StringValue': user_id
                }
            }
        )
        logger.info(f"Notification sent to user: {user_id}")
    except ClientError as e:
        logger.error(f"Error sending notification to {user_id}: {e.response['Error']['Message']}")

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

