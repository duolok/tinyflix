import json
import boto3
import os
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
user_actions_table = dynamodb.Table(os.environ['USER_ACTIONS_TABLE'])
movies_table = dynamodb.Table(os.environ['MOVIE_TABLE'])

def lambda_handler(event, context):
    logger.info("Received event: %s", event)
    user_id = event['user_id']

    try:
        actions = get_recent_user_actions(user_id)
        preferences = extract_user_preferences(actions)
        recommended_movies = generate_feed(preferences)
        
        logger.info("Recommended movies: %s", recommended_movies)
        return create_response(200, json.dumps(recommended_movies, default=str), cors=True)
    except Exception as e:
        logger.error("Error processing request: %s", e)
        return create_response(500, json.dumps({'error': str(e)}), cors=True)

def get_recent_user_actions(user_id):
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    
    response = user_actions_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('userId').eq(user_id) & 
                               boto3.dynamodb.conditions.Key('timestamp').gt(one_week_ago.isoformat())
    )
    logger.info("User actions: %s", response['Items'])
    return response['Items']

def extract_user_preferences(actions):
    preferences = defaultdict(set)
    logger.info("Extracting user preferences from actions")

    for action in actions:
        if action['action'] == 'rating':
            update_preferences_from_rating(action, preferences)
        elif action['action'] == 'subscription':
            update_preferences_from_subscription(action, preferences)
        elif action['action'] == 'download':
            update_preferences_from_download(action, preferences)
    
    return preferences

def update_preferences_from_rating(action, preferences):
    movie_id = action['movieId']
    movie = get_movie(movie_id)
    preferences['genres'].update(movie.get('genres', []))
    preferences['actors'].update(movie.get('actors', []))
    preferences['directors'].update(movie.get('directors', []))
    logger.info("Updated preferences from rating action: %s", preferences)

def update_preferences_from_subscription(action, preferences):
    criteria = action['details'].get('subscriptionCriteria', {}).get('M', {})
    
    genres = [item['S'] for item in criteria.get('genres', {}).get('L', [])]
    actors = [item['S'] for item in criteria.get('actors', {}).get('L', [])]
    directors = [item['S'] for item in criteria.get('directors', {}).get('L', [])]

    preferences['genres'].update(genres)
    preferences['actors'].update(actors)
    preferences['directors'].update(directors)

    logger.info("Updated preferences from subscription action: %s", preferences)


def update_preferences_from_download(action, preferences):
    movie_id = action['movieId']
    movie = get_movie(movie_id)
    preferences['downloaded'].add(movie_id)
    
    if 'genres' in movie:
        preferences['genres'].update(movie.get('genres', []))
    
    logger.info("Updated preferences from download action: %s", preferences)

def get_movie(movie_id):
    logger.info("Fetching movie details for movie ID: %s", movie_id)
    
    response = movies_table.get_item(Key={'name': movie_id})
    movie = response.get('Item', {})
    
    logger.info("Movie details: %s", movie)
    return movie

def generate_feed(preferences):
    logger.info("Generating recommendations based on preferences: %s", preferences)
    
    response = movies_table.scan()
    movies = response['Items']
    
    movie_scores = calculate_movie_scores(movies, preferences)
    sorted_movies = sort_movies_by_score(movie_scores)
    
    logger.info("Top recommended movies: %s", sorted_movies[:5])
    return sorted_movies[:5]

def calculate_movie_scores(movies, preferences):
    logger.info("Calculating scores for movies")

    movie_scores = []

    for movie in movies:
        score = 0
        score += sum(3 for genre in preferences['genres'] if genre in movie.get('genres', []))
        score += sum(2 for actor in preferences['actors'] if actor in movie.get('actors', []))
        score += sum(1 for director in preferences['directors'] if director in movie.get('directors', []))
        
        if score > 0:
            movie_scores.append({'movie': movie, 'score': score})
            logger.info("Calculated score for movie %s: %d", movie['name'], score)

    return movie_scores

def sort_movies_by_score(movie_scores):
    sorted_scores = sorted(movie_scores, key=lambda x: x['score'], reverse=True)
    return sorted_scores

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
