from constructs import Construct
import aws_cdk as core
from aws_cdk import (
    Duration,
    Stack,
    BundlingOptions,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_s3 as s3,
    aws_logs as logs,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_s3_notifications as s3n
)
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion

class TinyflixBackStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        movies_table = dynamodb.Table(
            self, "MoviesTable",
            table_name="tinyflixMoviesTable",
            partition_key=dynamodb.Attribute(
                name="name",
                type=dynamodb.AttributeType.STRING
            ),
            read_capacity=1,
            write_capacity=1
        )

        movies_table.add_global_secondary_index(
            index_name="TitleIndex",
            partition_key=dynamodb.Attribute(name="title", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="releaseDate", type=dynamodb.AttributeType.STRING)
        )

        movies_table.add_global_secondary_index(
            index_name="ActorsIndex",
            partition_key=dynamodb.Attribute(name="actors", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="releaseDate", type=dynamodb.AttributeType.STRING)
        )

        movies_table.add_global_secondary_index(
            index_name="DirectorsIndex",
            partition_key=dynamodb.Attribute(name="directors", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="releaseDate", type=dynamodb.AttributeType.STRING)
        )

        movies_table.add_global_secondary_index(
            index_name="GenresIndex",
            partition_key=dynamodb.Attribute(name="genres", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="releaseDate", type=dynamodb.AttributeType.STRING)
        )

        movies_table.add_global_secondary_index(
            index_name="DescptIndex",
            partition_key=dynamodb.Attribute(name="description", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="releaseDate", type=dynamodb.AttributeType.STRING)
        )

        movie_bucket = s3.Bucket(
            self, "tinyflixMovieBucket",
            bucket_name="serverless-movie-bucket",
        )

        lambda_role = iam.Role(
            self, "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )

        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )

        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:DescribeTable",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem"
                ],
                resources=[movies_table.table_arn]
            )
        )

        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject",
                    "s3:ListBucket"
                ],
                resources=[movie_bucket.bucket_arn, f"{movie_bucket.bucket_arn}/*"]
            )
        )

        index_arns = [
            f"{movies_table.table_arn}/index/TitleIndex",
            f"{movies_table.table_arn}/index/DescptIndex",
            f"{movies_table.table_arn}/index/ActorsIndex",
            f"{movies_table.table_arn}/index/DirectorsIndex",
            f"{movies_table.table_arn}/index/GenresIndex",
        ]

        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:Query"
                ],
                resources=index_arns
            )
        )

        def create_lambda(id, handler, include_dir, layers):
            print(f"Creating Lambda function with id: {id}, handler: {handler}, directory: {include_dir}")
            function = _lambda.Function(
                self, id,
                runtime=_lambda.Runtime.PYTHON_3_9,
                layers=layers,
                handler=handler,
                code=_lambda.Code.from_asset(
                    include_dir,
                    bundling=BundlingOptions(
                        image=_lambda.Runtime.PYTHON_3_9.bundling_image,
                        command=[
                            "bash", "-c",
                            "pip install --no-cache -r requirements.txt -t /asset-output && cp -r . /asset-output"
                        ],
                    ),
                ),
                memory_size=128,
                timeout=Duration.seconds(30),
                environment={
                    'MOVIE_TABLE': movies_table.table_name,
                    'MOVIE_BUCKET': movie_bucket.bucket_name
                },
                role=lambda_role,
                log_retention=logs.RetentionDays.ONE_WEEK
            )
            fn_url = function.add_function_url(
                auth_type=_lambda.FunctionUrlAuthType.NONE,
                cors=_lambda.FunctionUrlCorsOptions(
                    allowed_origins=["*"]
                )
            )
            
            return function

        model_layer = PythonLayerVersion(
            self, 'ModelLayer',
            entry='src/models',
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9]
        )

        service_layer = PythonLayerVersion(
            self, 'ServiceLayer',
            entry='src/services',
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9]
        )
        
        util_layer = PythonLayerVersion(
            self, 'UtilityLayer',
            entry='src/utility',
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9]
        )

        ffmpeg_layer = _lambda.LayerVersion(
            self, "ffmpegLayer",
            code=_lambda.Code.from_asset("src/transcoder-layer.zip"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9]
        )

        upload_metadata_lambda = create_lambda(
            "uploadMovieMetadata",
            "upload_metadata.lambda_handler",
            "src/lambda/upload_movie_metadata",
            [util_layer, service_layer, model_layer]
        )

        upload_file_lambda = create_lambda(
            "uploadMovieFile",
            "upload_file.lambda_handler",
            "src/lambda/upload_movie_file",
            [util_layer, service_layer, model_layer]
        )

        download_file_lambda = create_lambda(
            "downloadMovieFile",
            "download_file.lambda_handler",
            "src/lambda/download_movie_file",
            [util_layer, service_layer, model_layer]
        )

        get_movies_lambda = create_lambda(
            "getAllMovies",
            "get_movies.lambda_handler",
            "src/lambda/get_all_movies",
            [util_layer, service_layer, model_layer]
        )

        get_movie_lambda = create_lambda(
            "getMovie",
            "get_movie.lambda_handler",
            "src/lambda/get_movie",
            [util_layer, service_layer, model_layer]
        )

        delete_metadata_lambda = create_lambda(
            "deleteMovieMetadata",
            "delete_metadata.lambda_handler",
            "src/lambda/delete_movie_metadata",
            [util_layer, service_layer, model_layer]
        )

        delete_file_lambda = create_lambda(
            "deleteMovieFile",
            "delete_file.lambda_handler",
            "src/lambda/delete_movie_file",
            [util_layer, service_layer, model_layer]
        )

        search_movies_lambda = create_lambda(
            "searchAllMovies",
            "search_movies.lambda_handler",
            "src/lambda/search_all_movies",
            [util_layer, service_layer, model_layer]
        )

        update_movie_lambda = create_lambda(
            "updateMovie",
            "update_movie.lambda_handler",
            "src/lambda/update_movie",
            [util_layer, service_layer, model_layer]
        )

        transcode_movie_lambda = create_lambda(
            "transcodeMovie",
            "transcode.lambda_handler",
            "src/lambda/transcode_movie",
            [ffmpeg_layer, util_layer, service_layer, model_layer]
        )

        # Add S3 event notification to trigger transcode lambda
        movie_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(transcode_movie_lambda)
        )

        core.CfnOutput(self, "MovieBucketName", value=movie_bucket.bucket_name)

