import asyncio
import json
import os
import tempfile
import logging
import requests

from botocore.client import BaseClient
from fastapi import HTTPException
from S3Client import upload_files_to_s3
from harvest_repository import HarvestRepository
from models import Harvest
from schema.input import LISSRequest

LISS_ENDPOINT_URL = os.environ['LISS_ENDPOINT_URL']
LISS_ENDPOINT_USERNAME = os.environ['LISS_ENDPOINT_USERNAME']
LISS_ENDPOINT_KEY = os.environ['LISS_ENDPOINT_KEY']

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def harvest_liss_metadata(request: LISSRequest,
                                harvest_repo: HarvestRepository,
                                harvest_status: Harvest,
                                s3client: BaseClient):
    try:
        id_list = get_liss_id_list()
    except requests.exceptions.RequestException as e:
        error_message = f"Harvest failed due to API error from LISS API: {e}."
        harvest_repo.update_harvest_failed(harvest_status.harvest_id,
                                           error_message=error_message)
        logging.error(error_message)
        raise HTTPException(status_code=500, detail=error_message)

    with tempfile.TemporaryDirectory() as temp_dir:
        tasks = [fetch_and_save_metadata(pid, temp_dir) for pid in id_list]
        await asyncio.gather(*tasks)

        upload_files_to_s3(s3client, temp_dir, request.bucket_name)
        harvest_repo.update_harvest_success(harvest_status.harvest_id)


async def fetch_and_save_metadata(pid, temp_dir):
    metadata_file = await asyncio.to_thread(fetch_metadata, pid)
    save_metadata(pid, metadata_file, temp_dir)


def get_liss_id_list():
    """ Retrieves id's of all exposed liss datasets.

    :return:
    """
    response = requests.get(LISS_ENDPOINT_URL, auth=(
        LISS_ENDPOINT_USERNAME, LISS_ENDPOINT_KEY))
    response.raise_for_status()
    json_data = response.json()

    return [item["id"] for item in json_data]


def fetch_metadata(liss_id):
    """

    :param liss_id:
    :return:
    """
    url = LISS_ENDPOINT_URL + f'?id={liss_id}'
    try:
        return requests.get(
            url, auth=(LISS_ENDPOINT_USERNAME, LISS_ENDPOINT_KEY)).json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to retrieve data for id {liss_id}: {e}")


def save_metadata(liss_id, data, temp_dir):
    file_name = f"{liss_id}.json"
    output_file = os.path.join(temp_dir, file_name)
    with open(output_file, "w") as f:
        json.dump(data, f)
    logger.info(f"Data for id {liss_id} saved to {file_name}")
