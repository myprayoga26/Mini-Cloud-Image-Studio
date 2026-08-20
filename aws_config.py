import boto3
from botocore.exceptions import ClientError


# LocalStack dari komputer host biasanya tersedia di port 4566.
LOCALSTACK_ENDPOINT = "http://localhost:4566"
AWS_REGION = "us-east-1"

# Credential dummy hanya untuk simulasi LocalStack.
AWS_ACCESS_KEY_ID = "test"
AWS_SECRET_ACCESS_KEY = "test"

BUCKET_NAME = "image-studio-bucket"
DYNAMODB_TABLE_NAME = "ImageMetadata"


def get_s3_client():
    """Membuat client S3 yang diarahkan ke LocalStack."""
    return boto3.client(
        "s3",
        endpoint_url=LOCALSTACK_ENDPOINT,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def get_dynamodb_resource():
    """Membuat resource DynamoDB yang diarahkan ke LocalStack."""
    return boto3.resource(
        "dynamodb",
        endpoint_url=LOCALSTACK_ENDPOINT,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def get_dynamodb_client():
    """Membuat client DynamoDB."""
    return boto3.client(
        "dynamodb",
        endpoint_url=LOCALSTACK_ENDPOINT,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def ensure_resources():
    """
    Memastikan bucket S3 dan table DynamoDB tersedia.
    Fungsi ini dipanggil saat aplikasi pertama kali dijalankan.
    """
    s3 = get_s3_client()

    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
    except ClientError:
        # LocalStack tidak memerlukan ACL atau permission AWS sungguhan.
        s3.create_bucket(Bucket=BUCKET_NAME)

    dynamodb = get_dynamodb_client()

    try:
        dynamodb.describe_table(TableName=DYNAMODB_TABLE_NAME)
    except dynamodb.exceptions.ResourceNotFoundException:
        dynamodb.create_table(
            TableName=DYNAMODB_TABLE_NAME,
            KeySchema=[
                {"AttributeName": "image_id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "image_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        waiter = dynamodb.get_waiter("table_exists")
        waiter.wait(TableName=DYNAMODB_TABLE_NAME)
