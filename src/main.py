import tempfile
import logging

from fastapi import FastAPI
from LISS_harvester import get_liss_id_list, get_and_save_data
from S3Client import get_s3_client, upload_files_to_s3
from harvester import harvest_oai_pmh
from schema.input import HarvestRequest, LISSRequest
from version import get_version

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

s3client = get_s3_client()

@app.get("/version")
async def info():
    result = get_version()
    return {"version": result}


@app.post("/start_liss_harvest")
async def start_liss_harvest(request: LISSRequest):
    logger.info(f"Received request to start LISS harvest with data: {request}")

    id_list = get_liss_id_list()

    with tempfile.TemporaryDirectory() as temp_dir:
        for pid in id_list:
            get_and_save_data(
                pid,
                "https://www.oai-pmh.centerdata.nl/lissdata_json/?id={}",
                temp_dir
            )
        upload_files_to_s3(s3client, temp_dir, request.bucket_name)

    return {"message": "Harvest started"}


@app.post("/start_harvest")
async def start_harvest(request: HarvestRequest):
    # TODO: Handle bucket not existing.
    logger.info(
        f"Received request to start harvest with data: {request}")

    params = {
        'verb': request.verb,
        'metadataPrefix': request.metadata_prefix,
    }

    if request.oai_set is not None:
        params['set'] = request.oai_set

    with tempfile.TemporaryDirectory() as temp_dir:
        harvest_oai_pmh(request.oai_endpoint, temp_dir, params, request.verb)
        upload_files_to_s3(s3client, temp_dir, request.bucket_name)
    return {"message": "Harvest started"}
