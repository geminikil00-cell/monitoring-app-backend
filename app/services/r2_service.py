try:
    import boto3
    from botocore.config import Config
except ImportError:
    boto3 = None
    Config = None
from app.core.config import settings

def get_s3_client():
    if boto3 is None or Config is None:
        raise RuntimeError("boto3 is not installed")
    if not settings.R2_ENDPOINT_URL and settings.R2_ACCOUNT_ID:
        endpoint = f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    else:
        endpoint = settings.R2_ENDPOINT_URL
    return boto3.client(
        's3',
        endpoint_url=endpoint or None,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID or "mock_key",
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY or "mock_secret",
        config=Config(signature_version='s3v4')
    )

def generate_presigned_put(key: str, content_type: str = "image/jpeg") -> str:
    try:
        s3 = get_s3_client()
        return s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={'Bucket': settings.R2_BUCKET_NAME, 'Key': key, 'ContentType': content_type},
            ExpiresIn=3600
        )
    except Exception:
        return f"https://mock.r2.cloudflarestorage.com/{settings.R2_BUCKET_NAME}/{key}"

def generate_presigned_get(key: str) -> str:
    try:
        s3 = get_s3_client()
        return s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': settings.R2_BUCKET_NAME, 'Key': key},
            ExpiresIn=3600
        )
    except Exception:
        return f"https://mock.r2.cloudflarestorage.com/{settings.R2_BUCKET_NAME}/{key}"
