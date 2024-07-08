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
    aws_sns as sns,
    aws_s3_notifications as s3n,
    aws_lambda_event_sources as lambda_event_sources,
    aws_sqs as sqs,
    aws_apigateway as apigateway,
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
            write_capacity=1,
            stream=dynamodb.StreamViewType.NEW_IMAGE  
        )

        subscriptions_table = dynamodb.Table(
            self, "SubscriptionsTable",
            table_name="tinyflixSubscriptionsTable",
            partition_key=dynamodb.Attribute(
                name="userId",
                type=dynamodb.AttributeType.STRING
            ),
            read_capacity=1,
            write_capacity=1
        )

        ratings_table = dynamodb.Table(
            self, "RatingTable",
            table_name="tinyflixRatingTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            read_capacity=1,
            write_capacity=1
        )

        user_actions_table = dynamodb.Table(
            self, "UserActionsTable",
            table_name="tinyflixUserActionsTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            read_capacity=1,
            write_capacity=1,
            stream=dynamodb.StreamViewType.NEW_IMAGE  
        )

        top_movies_table = dynamodb.Table(
            self, "TopMoviesTable",
            table_name="tinyflixTopMoviesTable",
            partition_key=dynamodb.Attribute(
                name="userId",
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

        user_actions_table.add_global_secondary_index(
            index_name="EmailIndex",
            partition_key=dynamodb.Attribute(name="email", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="timestamp", type=dynamodb.AttributeType.STRING)
        )

        movie_bucket = s3.Bucket(
            self, "tinyflixMovieBucket",
            bucket_name="serverless-movie-bucket",
        )

        notification_topic = sns.Topic(
            self, "NotificationTopic",
            topic_name="tinyflixNotificationTopic"
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
                    "dynamodb:DeleteItem",
                    "dynamodb:ListStreams",
                    "dynamodb:GetRecords",
                    "dynamodb:GetShardIterator",
                    "dynamodb:DescribeStream",
                    "dynamodb:ListStreams"
                ],
                resources=[
                    movies_table.table_arn,
                    subscriptions_table.table_arn,
                    ratings_table.table_arn,
                    user_actions_table.table_arn,
                    top_movies_table.table_arn,
                ]
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

        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "sns:Publish",
                    "sns:Subscribe",
                    "sns:Unsubscribe",
                    "sns:ListSubscriptionsByTopic"  
                ],
                resources=[notification_topic.topic_arn]
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


        upload_metadata_queue = sqs.Queue(self, "UploadMetadataQueue", queue_name="upload-metadata-queue")
        upload_file_queue = sqs.Queue(self, "UploadFileQueue", queue_name="upload-file-queue")
        delete_metadata_queue = sqs.Queue(self, "DeleteMetadataQueue", queue_name="delete-metadata-queue")
        delete_file_queue = sqs.Queue(self, "DeleteFileQueue", queue_name="delete-file-queue")
        download_file_queue = sqs.Queue(self, "DownloadFileQueue", queue_name="download-file-queue")


        def create_lambda(id, handler, include_dir, layers, queue=None):
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
                    'SUBSCRIPTIONS_TABLE': subscriptions_table.table_name,
                    'RATINGS_TABLE': ratings_table.table_name,
                    'USER_ACTIONS_TABLE': user_actions_table.table_name,
                    'TOP_MOVIES_TABLE': top_movies_table.table_name,
                    'MOVIE_BUCKET': movie_bucket.bucket_name,
                    'NOTIFICATION_TOPIC_ARN': notification_topic.topic_arn
                },
                role=lambda_role,
                log_retention=logs.RetentionDays.ONE_WEEK
            )
            if queue:
                function.add_event_source(lambda_event_sources.SqsEventSource(queue))

            fn_url = function.add_function_url(
                auth_type=_lambda.FunctionUrlAuthType.NONE,
                cors=_lambda.FunctionUrlCorsOptions(
                    allowed_origins=["*"]
                )
            )
            return function
        
        def create_transcode_lambda(id, handler, include_dir, layers):
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
                memory_size=1024,
                timeout=Duration.seconds(300),
                environment={
                    'MOVIE_TABLE': movies_table.table_name,
                    'SUBSCRIPTIONS_TABLE': subscriptions_table.table_name,
                    'RATINGS_TABLE': ratings_table.table_name,
                    'USER_ACTIONS_TABLE': user_actions_table.table_name,
                    'TOP_MOVIES_TABLE': top_movies_table.table_name,
                    'MOVIE_BUCKET': movie_bucket.bucket_name,
                    'NOTIFICATION_TOPIC_ARN': notification_topic.topic_arn
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

        upload_metadata_lambda = create_lambda(
            "uploadMovieMetadata",
            "upload_metadata.lambda_handler",
            "src/lambda/upload_movie_metadata",
            [util_layer, service_layer, model_layer],
            upload_metadata_queue
        )

        upload_file_lambda = create_lambda(
            "uploadMovieFile",
            "upload_file.lambda_handler",
            "src/lambda/upload_movie_file",
            [util_layer, service_layer, model_layer],
            upload_file_queue
        )

        download_file_lambda = create_lambda(
            "downloadMovieFile",
            "download_file.lambda_handler",
            "src/lambda/download_movie_file",
            [util_layer, service_layer, model_layer],
            download_file_queue
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
            [util_layer, service_layer, model_layer],
            delete_metadata_queue
        )

        delete_file_lambda = create_lambda(
            "deleteMovieFile",
            "delete_file.lambda_handler",
            "src/lambda/delete_movie_file",
            [util_layer, service_layer, model_layer],
            delete_file_queue
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

        subscribe_content_lambda = create_lambda(
            "subscribeToContent",
            "subscribe.lambda_handler",
            "src/lambda/subscribe_to_content",
            [util_layer, service_layer, model_layer]
        )

        unsubscribe_content_lambda = create_lambda(
            "unsubscribeFromContent",
            "unsubscribe.lambda_handler",
            "src/lambda/unsubscribe_from_content",
            [util_layer, service_layer, model_layer]
        )

        get_subscriptions_lambda = create_lambda(
            "getSubscriptions",
            "get_subscriptions.lambda_handler",
            "src/lambda/get_subscriptions",
            [util_layer, service_layer, model_layer]
        )

        generate_feed_lambda = create_lambda(
            "generateFeed",
            "feed.lambda_handler",
            "src/lambda/generate_feed",
            [util_layer, service_layer, model_layer]
        )

        transcode_movie_lambda = create_transcode_lambda(
            "transcodeMovie",
            "transcode.lambda_handler",
            "src/lambda/transcode_movie",
            [ffmpeg_layer, util_layer, service_layer, model_layer]
        )

        notify_users_lambda = create_lambda(
            "notifyUsers",
            "notify.lambda_handler",
            "src/lambda/notify_users",
            [util_layer, service_layer, model_layer]
        )

        rate_movie_lambda = create_lambda(
            "rateMovie",
            "rate.lambda_handler",
            "src/lambda/rate_movie",
            [util_layer, service_layer, model_layer]
        )

        get_feed_movies_lambda = create_lambda(
            "getFeedMovies",
            "get_feed_movies.lambda_handler",
            "src/lambda/get_feed_movies",
            [util_layer, service_layer, model_layer]
        )

        movie_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(transcode_movie_lambda)
        )

        notify_users_lambda.add_event_source(
            lambda_event_sources.DynamoEventSource(
                movies_table,
                starting_position=_lambda.StartingPosition.TRIM_HORIZON,
                batch_size=10,
                retry_attempts=3
            )
        )

        generate_feed_lambda.add_event_source(
            lambda_event_sources.DynamoEventSource(
                user_actions_table,
                starting_position=_lambda.StartingPosition.TRIM_HORIZON,
                batch_size=10,
                retry_attempts=3
            )
        )

        api = apigateway.RestApi(self, "tinygateway", rest_api_name="Tinyflix Gateway", description="This service serves the Tinyflix application.")

        content_management = api.root.add_resource("content-management")
        movies = api.root.add_resource("movies")

        content_management.add_method("PUT", apigateway.LambdaIntegration(subscribe_content_lambda))

        unsubscribe = content_management.add_resource("unsubscribe")
        unsubscribe.add_method("POST", apigateway.LambdaIntegration(unsubscribe_content_lambda))

        get_subscriptions = content_management.add_resource("get_subscriptions")
        get_subscriptions.add_method("GET", apigateway.LambdaIntegration(get_subscriptions_lambda))

        get_feed = content_management.add_resource("get-feed")
        get_feed.add_method("GET", apigateway.LambdaIntegration(get_feed_movies_lambda))

        upload_metadata = movies.add_resource("upload-movie-metadata")
        upload_metadata.add_method("POST", apigateway.LambdaIntegration(upload_metadata_lambda))

        upload_file = movies.add_resource("upload-movie-file")
        upload_file.add_method("PUT", apigateway.LambdaIntegration(upload_file_lambda))

        delete_metadata = movies.add_resource("delete-movie-metadata")
        delete_metadata.add_method("DELETE", apigateway.LambdaIntegration(delete_metadata_lambda))

        delete_file = movies.add_resource("delete-movie-file")
        delete_file.add_method("DELETE", apigateway.LambdaIntegration(delete_file_lambda))

        download_file = movies.add_resource("download-movie-file")
        download_file.add_method("GET", apigateway.LambdaIntegration(download_file_lambda))

        get_movies = movies.add_resource("get-all-movies")
        get_movies.add_method("GET", apigateway.LambdaIntegration(get_movies_lambda))

        get_movie = movies.add_resource("get-movie")
        get_movie.add_method("GET", apigateway.LambdaIntegration(get_movie_lambda))

        rate_movie = movies.add_resource("rate-movie")
        rate_movie.add_method("PATCH", apigateway.LambdaIntegration(rate_movie_lambda))

        search_movies = movies.add_resource("search")
        search_movies.add_method("GET", apigateway.LambdaIntegration(search_movies_lambda))

        update_movie = movies.add_resource("update-movie")
        update_movie.add_method("PATCH", apigateway.LambdaIntegration(update_movie_lambda))






        core.CfnOutput(self, "MovieBucketName", value=movie_bucket.bucket_name)
        core.CfnOutput(self, "NotificationTopicArn", value=notification_topic.topic_arn)
        core.CfnOutput(self, "ApiGatewayUrl", value=api.url)
