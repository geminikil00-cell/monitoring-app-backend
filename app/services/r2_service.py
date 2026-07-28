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

def is_r2_configured() -> bool:
    """Check if R2 credentials are actually configured (not empty strings)"""
    return bool(
        settings.R2_ACCESS_KEY_ID and 
        settings.R2_SECRET_ACCESS_KEY and 
        (settings.R2_ACCOUNT_ID or settings.R2_ENDPOINT_URL)
    )

def generate_presigned_put(key: str, content_type: str = "image/jpeg") -> str:
    if not is_r2_configured():
        return None
    try:
        s3 = get_s3_client()
        return s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={'Bucket': settings.R2_BUCKET_NAME, 'Key': key, 'ContentType': content_type},
            ExpiresIn=3600
        )
    except Exception:
        return None

def upload_file(key: str, data: bytes, content_type: str = "application/octet-stream") -> bool:
    if not is_r2_configured():
        return False
    try:
        s3 = get_s3_client()
        s3.put_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=key,
            Body=data,
            ContentType=content_type
        )
        return True
    except Exception:
        return False

def generate_presigned_get(key: str) -> str:
    if not is_r2_configured():
        return None
    try:
        s3 = get_s3_client()
        return s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': settings.R2_BUCKET_NAME, 'Key': key},
            ExpiresIn=3600
        )
    except Exception:
        return None

def delete_file(key: str) -> bool:
    if not is_r2_configured():
        return False
    try:
        s3 = get_s3_client()
        s3.delete_object(Bucket=settings.R2_BUCKET_NAME, Key=key)
        return True
    except Exception:
        return False

def delete_files(keys: list) -> int:
    if not is_r2_configured() or not keys:
        return 0
    try:
        s3 = get_s3_client()
        objects = [{'Key': k} for k in keys]
        s3.delete_objects(Bucket=settings.R2_BUCKET_NAME, Delete={'Objects': objects})
        return len(keys)
    except Exception:
        return 0
