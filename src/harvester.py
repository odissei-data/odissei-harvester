import asyncio
import json
import os
import tempfile
import logging
import requests

from botocore.client import BaseClient
from fastapi import HTTPException
from S3Client import upload_files_to_s3
from harvest_client import HarvestClient
from harvest_repository import HarvestRepository
from models import Harvest
from schema.input import HarvestRequest

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def harvest_metadata(request: HarvestRequest,
                           harvest_client: HarvestClient,
                           harvest_repo: HarvestRepository,
                           harvest_status: Harvest,
                           s3client: BaseClient):
    try:
        id_list = harvest_client.get_id_list()
    except requests.exceptions.RequestException as e:
        error_message = f"Harvest failed due to API error from API: {e}."
        harvest_repo.update_harvest_failed(harvest_status.harvest_id,
                                           error_message=error_message)
        logging.error(error_message)
        raise HTTPException(status_code=500, detail=error_message)

    with tempfile.TemporaryDirectory() as temp_dir:
        tasks = [fetch_and_save_metadata(pid, temp_dir, harvest_client) for pid
                 in id_list]
        await asyncio.gather(*tasks)

        upload_files_to_s3(s3client, temp_dir, request.bucket_name)
        harvest_repo.update_harvest_success(harvest_status.harvest_id)


async def fetch_and_save_metadata(pid, temp_dir, harvest_client):
    dataset_metadata = await asyncio.to_thread(harvest_client.fetch_metadata,
                                               pid)
    save_metadata(pid, dataset_metadata, temp_dir)


def save_metadata(dataset_id, dataset_metadata, temp_dir):
    file_name = f"{dataset_id}.json"
    output_file = os.path.join(temp_dir, file_name)
    with open(output_file, "w") as f:
        json.dump(dataset_metadata, f)
    logger.info(f"Data for id {dataset_id} saved to {file_name}")
