import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class S3Storage:
    def __init__(self):
        self.s3_client = None
        if settings.S3_ACCESS_KEY and settings.S3_SECRET_KEY:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION,
                endpoint_url=settings.S3_ENDPOINT
            )
        self.bucket_name = settings.S3_BUCKET

    def upload_file(self, file_content, object_name):
        """Upload a file to an S3 bucket"""
        if not self.s3_client:
            logger.error("S3 client not initialized. Check credentials.")
            return False

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=file_content
            )
            return True
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            return False

    def get_file_url(self, object_name, expiration=3600):
        """Generate a presigned URL to share an S3 object"""
        if not self.s3_client:
            return None

        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            logger.error(f"S3 URL generation error: {e}")
            return None

storage = S3Storage()
