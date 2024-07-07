import json
import boto3
import os
from datetime import datetime, timedelta
from collections import defaultdict

dynamodb = boto3.resource('dynamodb')
user_actions_table = dynamodb.Table(os.environ['USER_ACTIONS_TABLE'])
movies_table = dynamodb.Table(os.environ['MOVIE_TABLE'])

def lambda_handler(event, context):
    user_id = event['user_id']

    actions = get_recent_user_actions(user_id)
    preferences = extract_user_preferences(actions)
    recommended_movies = generate_recommendations(preferences)

    return create_response(200, json.dumps(recommended_movies, default=str), cors=True)

def get_recent_user_actions(user_id):
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    response = user_actions_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('userId').eq(user_id) & 
                               boto3.dynamodb.conditions.Key('timestamp').gt(one_week_ago.isoformat())
    )
    return response['Items']

def extract_user_preferences(actions):
    preferences = defaultdict(set)

    for action in actions:
        if action['action'] == 'rating':
            movie_id = action['movieId']
            movie = get_movie(movie_id)
            preferences['genres'].update(movie.get('genres', []))
            preferences['actors'].update(movie.get('actors', []))
            preferences['directors'].update(movie.get('directors', []))
        elif action['action'] == 'subscription':
            criteria = action['details'].get('subscriptionCriteria', {})
            preferences['genres'].update(criteria.get('genres', []))
            preferences['actors'].update(criteria.get('actors', []))
            preferences['directors'].update(criteria.get('directors', []))
        elif action['action'] == 'download':
            movie_id = action['movieId']
            movie = get_movie(movie_id)
            preferences['downloaded'].add(movie_id)
    return preferences

def get_movie(movie_id):
    response = movies_table.get_item(Key={'name': movie_id})
    return response.get('Item', {})

def generate_recommendations(preferences):
    response = movies_table.scan()
    movies = response['Items']
    
    movie_scores = calculate_movie_scores(movies, preferences)
    sorted_movies = sort_movies_by_score(movie_scores)
    return sorted_movies[:5]

def calculate_movie_scores(movies, preferences):
    movie_scores = []

    for movie in movies:
        score = 0
        score += sum(1 for genre in preferences['genres'] if genre in movie.get('genres', []))
        score += sum(1 for actor in preferences['actors'] if actor in movie.get('actors', []))
        score += sum(1 for director in preferences['directors'] if director in movie.get('directors', []))
        if movie['name'] in preferences['downloaded']:
            score += 1
        
        if score > 0:
            movie_scores.append({'movie': movie, 'score': score})
    return movie_scores

def sort_movies_by_score(movie_scores):
    return sorted(movie_scores, key=lambda x: x['score'], reverse=True)

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

