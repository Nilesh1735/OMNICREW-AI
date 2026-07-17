import os
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

def archive_to_s3(content: str, object_name: str):
    """
    Safely archives raw AI output to an AWS S3 bucket.
    Fails silently if AWS credentials are not provided, ensuring local dev isn't broken.
    """
    aws_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    bucket_name = os.getenv("AWS_S3_BUCKET_NAME")

    # Fail-safe: If no keys or bucket are provided, skip S3 and return
    if not all([aws_key, aws_secret, bucket_name]):
        logger.info("AWS S3 credentials not found. Skipping S3 archival.")
        return False

    try:
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
            region_name=aws_region
        )
        
        # Upload the content as a JSON file
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_name,
            Body=content.encode('utf-8'),
            ContentType='application/json'
        )
        logger.info(f"Successfully archived raw payload to S3: {object_name}")
        return True
        
    except ClientError as e:
        logger.error(f"Failed to upload to S3: {e}")
        return False