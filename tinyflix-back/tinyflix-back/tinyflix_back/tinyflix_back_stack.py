from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    RemovalPolicy,
)
from constructs import Construct

class TinyflixBackStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB table
        table = dynamodb.Table(
            self, "MoviesTable",
            partition_key=dynamodb.Attribute(
                name="MovieID",
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        bucket = s3.Bucket(
            self, "MovieBucket",
            removal_policy=RemovalPolicy.DESTROY
        )

        upload_metadata_lambda = _lambda.Function(
            self, 'UploadMetadataFunction',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='upload_metadata.lambda_handler',
            environment={
                'MOVIE_TABLE': table.table_name
            }
        )

        upload_file_lambda = _lambda.Function(
            self, 'UploadFileFunction',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='upload_file.lambda_handler',
            environment={
                'MOVIE_BUCKET': bucket.bucket_name
            }
        )

        generate_presigned_url = _lambda.Function(
            self, 'GeneratePresignedUrlFunction',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='generate_presigned_url.lambda_handler',
        )


        download_file_lambda = _lambda.Function(
            self, 'DownloadFileFunction',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='download_file.lambda_handler',
            environment={
                'MOVIE_BUCKET': bucket.bucket_name
            }
        )

        table.grant_read_write_data(upload_metadata_lambda)
        bucket.grant_read_write(upload_file_lambda)
        bucket.grant_read(download_file_lambda)

