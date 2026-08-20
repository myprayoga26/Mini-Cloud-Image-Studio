import uuid
from aws_config import get_s3_client, BUCKET_NAME


def upload_bytes(data, original_filename, content_type, folder="originals"):
    """
    Upload bytes ke S3.

    Return:
        s3_key, image_id
    """
    image_id = str(uuid.uuid4())

    safe_name = original_filename.replace("/", "_").replace("\\", "_")
    s3_key = f"{folder}/{image_id}_{safe_name}"

    s3 = get_s3_client()
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=data,
        ContentType=content_type,
    )

    return s3_key, image_id


def download_bytes(s3_key):
    """Mengambil object dari S3 sebagai bytes."""
    s3 = get_s3_client()

    response = s3.get_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
    )

    return response["Body"].read()


def list_objects(prefix=""):
    """Mengambil daftar object dari bucket S3."""
    s3 = get_s3_client()

    response = s3.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=prefix,
    )

    return response.get("Contents", [])


def delete_object(s3_key):
    """Menghapus object dari S3."""
    s3 = get_s3_client()

    s3.delete_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
    )
