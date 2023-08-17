import boto3
import os
import logging

from fastapi import HTTPException

AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
S3_STORAGE_ENDPOINT = os.environ['S3_STORAGE_ENDPOINT']

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_s3_client():
    # Create an S3 client
    return boto3.client(
        's3',
        endpoint_url=S3_STORAGE_ENDPOINT,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def create_bucket_if_not_exists(s3_client, bucket_name):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except s3_client.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            s3_client.create_bucket(Bucket=bucket_name)
            logging.info(f"Created S3 bucket: {bucket_name}")
        else:
            logging.error(f"Error checking/creating bucket: {e}")


def upload_files_to_s3(s3_client, source_dir, bucket_name, prefix=''):
    failed_files = []
    create_bucket_if_not_exists(s3_client, bucket_name)
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            source_path = os.path.join(root, file)
            s3_key = os.path.join(prefix, file)

            try:
                s3_client.upload_file(source_path, bucket_name, s3_key)
                logging.info(
                    f"Uploaded {file} to S3 bucket: {bucket_name}"
                    f" with key: {s3_key}")
            except Exception as e:
                failed_files.append(file)
                logging.error(
                    f"Failed to upload {file} to S3 bucket: {bucket_name}"
                    f" with key: {s3_key}. Error: {e}")
    logger.info('Completed uploading harvested files to s3.')
    return failed_files
