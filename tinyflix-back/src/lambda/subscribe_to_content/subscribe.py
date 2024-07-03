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
        new_subscriptions = body['subscriptionCriteria']
        email = body['userId']  
        
        logger.info("Processing subscriptions for user: %s", user_id)
        
        response = table.get_item(Key={'userId': user_id})
        if 'Item' in response:
            existing_subscriptions = response['Item'].get('subscriptions', {
                'actors': [],
                'genres': [],
                'directors': []
            })
            logger.info("Existing subscriptions: %s", json.dumps(existing_subscriptions))
        else:
            existing_subscriptions = {
                'actors': [],
                'genres': [],
                'directors': []
            }
            logger.info("No existing subscriptions found, initializing new subscriptions")

        merged_subscriptions = merge_subscriptions(existing_subscriptions, new_subscriptions)
        logger.info("Merged subscriptions: %s", json.dumps(merged_subscriptions))
        
        table.update_item(
            Key={'userId': user_id},
            UpdateExpression="SET subscriptions = :subscriptions, email = :email",
            ExpressionAttributeValues={
                ':subscriptions': merged_subscriptions,
                ':email': email
            },
            ReturnValues="UPDATED_NEW"
        )

        subscribe_to_sns_topic(email, os.environ['NOTIFICATION_TOPIC_ARN'])
        
        logger.info("Successfully updated subscriptions for user: %s", user_id)
        return create_response(200, json.dumps('Subscription added successfully!'), cors=True)
    
    except ClientError as e:
        logger.error("DynamoDB ClientError: %s", e.response['Error']['Message'])
        return create_response(500, json.dumps('Error subscribing user: ' + e.response['Error']['Message']), cors=True)
    
    except Exception as e:
        logger.error("Exception: %s", str(e))
        return create_response(500, json.dumps('Error: ' + str(e)), cors=True)

def merge_subscriptions(existing_subscriptions, new_subscriptions):
    for key in new_subscriptions:
        if key in existing_subscriptions:
            existing_subscriptions[key] = list(set(existing_subscriptions[key] + new_subscriptions[key]))
        else:
            existing_subscriptions[key] = new_subscriptions[key]
    return existing_subscriptions

def subscribe_to_sns_topic(email, topic_arn):
    try:
        response = sns.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email
        )
        logger.info(f"Successfully subscribed {email} to topic {topic_arn}: {response['SubscriptionArn']}")
    except ClientError as e:
        logger.error(f"Error subscribing {email} to topic {topic_arn}: {e.response['Error']['Message']}")
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

