from S3Client import get_s3_client
from harvest_repository import HarvestRepository
from server import create_server

s3client = get_s3_client()

harvest_repo = HarvestRepository()

server = create_server(s3client, repository=harvest_repo)

