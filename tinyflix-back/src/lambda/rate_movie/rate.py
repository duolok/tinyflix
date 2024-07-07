from uuid import uuid1
import json
import boto3
import os
from decimal import Decimal
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
ratings_table = dynamodb.Table(os.environ['RATINGS_TABLE'])
movies_table = dynamodb.Table(os.environ['MOVIE_TABLE'])
user_actions_table = dynamodb.Table(os.environ['USER_ACTIONS_TABLE'])

def lambda_handler(event, context):
    try:
        print("Received event: ", json.dumps(event, indent=2))
        
        if 'body' not in event:
            raise ValueError("Missing 'body' in event")
        
        body = json.loads(event['body'], parse_float=Decimal)
        print("Parsed body: ", body)

        required_fields = ['email', 'movie_id', 'rating']
        for field in required_fields:
            if field not in body:
                raise ValueError(f"Missing required field: {field}")
        
        rating = body['rating']
        if not isinstance(rating, int) or rating < 1 or rating > 10:
            raise ValueError("Rating must be an integer between 1 and 10")
        
        rating_entry = {
            'id': str(uuid1()),
            'email': body['email'],
            'movieId': body['movie_id'],
            'rating': Decimal(rating),
            'timestamp': datetime.utcnow().isoformat()
        }

        ratings_table.put_item(Item=rating_entry)
        
        response = movies_table.get_item(Key={'name': body['movie_id']})
        if 'Item' not in response:
            raise ValueError("Movie not found")
        
        movie = response['Item']
        current_avg_rating = movie.get('avg_rating', Decimal(0))
        current_rate_count = movie.get('rate_count', 0)

        new_rate_count = current_rate_count + 1
        new_avg_rating = ((current_avg_rating * current_rate_count) + Decimal(rating)) / new_rate_count

        movies_table.update_item(
            Key={'name': body['movie_id']},
            UpdateExpression="SET avg_rating = :avg_rating, rate_count = :rate_count",
            ExpressionAttributeValues={
                ':avg_rating': new_avg_rating,
                ':rate_count': new_rate_count
            }
        )
    
        log_user_action(body['email'], 'rating', body['movie_id'], {'rating': rating})
        return create_response(200, json.dumps({'message': 'Rating added and movie stats updated successfully!'}, default=str), cors=True)

    except json.JSONDecodeError as e:
        print("JSON decode error: ", str(e))
        return create_response(400, json.dumps({'error': 'Invalid JSON format'}), cors=True)
    except ValueError as e:
        print("Value error: ", str(e))
        return create_response(400, json.dumps({'error': str(e)}), cors=True)
    except Exception as e:
        print("Exception: ", str(e))
        return create_response(500, json.dumps({'error': str(e)}), cors=True)

def log_user_action(user_id, action, movie_id, details):
    try:
        user_actions_table.put_item(
            Item={
                'id': str(uuid1()),
                'userId': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'action': action,
                'movieId': movie_id,
                'details': details
            }
        )
    except Exception as e:
        print(f"Error logging user action: {str(e)}")
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

