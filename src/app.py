import os
import database
from S3Client import get_s3_client
from harvest_repository import HarvestRepository
from server import create_server

AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
S3_STORAGE_ENDPOINT = os.environ['S3_STORAGE_ENDPOINT']

s3client = get_s3_client(secret_key=AWS_SECRET_ACCESS_KEY,
                         access_key=AWS_ACCESS_KEY_ID,
                         s3_storage_endpoint=S3_STORAGE_ENDPOINT)

harvest_repo = HarvestRepository()
database.Base.metadata.create_all(bind=database.engine)

server = create_server(s3client, repository=harvest_repo)
