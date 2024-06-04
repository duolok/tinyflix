import json
import os
from ..models import Movie
from ..services.dynamodb_service import DynamoDbService
from ..service.s3_service import S3Service
from ..config import config

dynamodb_service = DynamoDbService(config.movie_table)
s3_service = S3Service(config.movie_bucket)

def lambda_handler(event, context):
    pass
