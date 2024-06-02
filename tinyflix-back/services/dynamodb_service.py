import boto3
from boto3.dynamodb.conditions import Key
from models import Movie

class DynamoDbService:
    def __init__(self, table_name):
        self.client = boto3.resource('dynamodb')
        self.table = self.client.Table(table_name)

    def save_movie_metadata(self, movie):
        self.table.put_item(item=movie.to_dict())
    
    def get_movie_metadata(self, movie_id):
        response = self.table.get_item(Key={'id': movie_id}) 
        if 'Item' in response:
            item = response['Item']
            return Movie(item['id'], item['title'], item['genre'], item['director'], item['actors'], item.get('rating'), item['s3_path'])
        return None
    
    def delete_movie_metadata(self, movie_id):
        self.table.delete_item(Key={'id': movie_id})
