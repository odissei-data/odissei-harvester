import boto3
import os
import logging

AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
S3_STORAGE_ENDPOINT = os.environ['S3_STORAGE_ENDPOINT']


def get_s3_client():
    # Create an S3 client
    return boto3.client(
        's3',
        endpoint_url=S3_STORAGE_ENDPOINT,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def upload_files_to_s3(s3_client, source_dir, bucket_name, prefix=''):
    # Configure logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    for root, dirs, files in os.walk(source_dir):
        for file in files:
            source_path = os.path.join(root, file)
            s3_key = os.path.join(prefix, file)

            try:
                # Upload the file to the S3 bucket
                s3_client.upload_file(source_path, bucket_name, s3_key)
                logging.info(
                    f"Uploaded {file} to S3 bucket: {bucket_name}"
                    f" with key: {s3_key}")
            except Exception as e:
                logging.error(
                    f"Failed to upload {file} to S3 bucket: {bucket_name}"
                    f" with key: {s3_key}. Error: {e}")
