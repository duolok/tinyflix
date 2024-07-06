import json
import boto3
import os
import logging
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['SUBSCRIPTIONS_TABLE'])
sns = boto3.client('sns')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        logger.info("Received event: %s", json.dumps(event))
        
        body = json.loads(event['body'])
        user_id = body['userId']
        subscriptions_to_remove = body['subscriptionCriteria']
        email = body['userId']
        
        logger.info("Processing subscriptions removal for user: %s", user_id)
        
        response = table.get_item(Key={'userId': user_id})
        if 'Item' in response:
            existing_subscriptions = response['Item'].get('subscriptions', {
                'actors': {'L': []},
                'genres': {'L': []},
                'directors': {'L': []}
            })
            logger.info("Existing subscriptions: %s", json.dumps(existing_subscriptions))
            logger.info("Subscriptions to remove : %s", json.dumps(subscriptions_to_remove))
        else:
            return create_response(404, json.dumps('No subscriptions found for user.'), cors=True)

        updated_subscriptions = remove_subscriptions(existing_subscriptions, subscriptions_to_remove)
        logger.info("Updated subscriptions: %s", json.dumps(updated_subscriptions))
        
        table.update_item(
            Key={'userId': user_id},
            UpdateExpression="SET subscriptions = :subscriptions, email = :email",
            ExpressionAttributeValues={
                ':subscriptions': updated_subscriptions,
                ':email': email
            },
            ReturnValues="UPDATED_NEW"
        )

        unsubscribe_from_sns_topic(email, os.environ['NOTIFICATION_TOPIC_ARN'])
        
        logger.info("Successfully updated subscriptions for user: %s", user_id)
        return create_response(200, json.dumps('Subscription removed successfully!'), cors=True)
    
    except ClientError as e:
        logger.error("DynamoDB ClientError: %s", e.response['Error']['Message'])
        return create_response(500, json.dumps('Error unsubscribing user: ' + e.response['Error']['Message']), cors=True)
    
    except Exception as e:
        logger.error("Exception: %s", str(e))
        return create_response(500, json.dumps('Error: ' + str(e)), cors=True)

def remove_subscriptions(existing_subscriptions, subscriptions_to_remove):
    key_mapping = {
        'director': 'directors',
        'actor': 'actors',
        'genre': 'genres'
    }

    for key, values in subscriptions_to_remove.items():
        mapped_key = key_mapping.get(key, key)
        if mapped_key in existing_subscriptions:
            existing_subscriptions[mapped_key] = [
                sub for sub in existing_subscriptions[mapped_key]
                if sub not in (value['S'] for value in values)
            ]
    return existing_subscriptions

def unsubscribe_from_sns_topic(email, topic_arn):
    try:
        response = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
        subscriptions = response['Subscriptions']
        for subscription in subscriptions:
            if subscription['Endpoint'] == email:
                sns.unsubscribe(SubscriptionArn=subscription['SubscriptionArn'])
                logger.info(f"Successfully unsubscribed {email} from topic {topic_arn}")
                break
    except ClientError as e:
        logger.error(f"Error unsubscribing {email} from topic {topic_arn}: {e.response['Error']['Message']}")
        raise e

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

