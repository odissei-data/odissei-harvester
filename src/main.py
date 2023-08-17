import tempfile
import logging

import requests
from sqlalchemy.orm import Session

import crud
import models
from models import HarvestStatus
import xml.etree.ElementTree as ET

from fastapi import FastAPI, HTTPException, Depends
from LISS_harvester import get_liss_id_list, get_metadata, \
    save_metadata
from S3Client import get_s3_client, upload_files_to_s3
from database import engine, SessionLocal
from harvester import harvest_oai_pmh
from schema.harvest import HarvestBase
from schema.input import HarvestRequest, LISSRequest
from version import get_version

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()
s3client = get_s3_client()
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/version")
async def info():
    result = get_version()
    return {"version": result}


@app.get("/harvest_status/{harvest_id}", response_model=HarvestBase)
async def get_status(harvest_id: str, db: Session = Depends(get_db)):
    status = crud.get_harvest_status(db, harvest_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Harvest not found")
    return status


@app.post("/start_liss_harvest", response_model=HarvestBase)
async def start_liss_harvest(request: LISSRequest,
                             db: Session = Depends(get_db)):
    logger.info(f"Received request to start LISS harvest with data: {request}")

    harvest_status = crud.create_harvest(db)
    try:
        id_list = get_liss_id_list()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to retrieve data for LISS harvest: {e}")
        # Update harvest status to indicate failure
        crud.update_harvest_status(
            db,
            harvest_status.harvest_id,
            HarvestStatus.FAILED,
            error_message="Harvest failed due to API error from the LISS API."
        )
        raise HTTPException(status_code=500,
                            detail="Failed to retrieve data from external API")

    with tempfile.TemporaryDirectory() as temp_dir:
        for pid in id_list:
            data = get_metadata(pid)
            save_metadata(pid, data, temp_dir)

        failed_files = upload_files_to_s3(s3client, temp_dir,
                                          request.bucket_name)
        if failed_files:
            crud.create_failed_files(db, harvest_status.harvest_id,
                                     failed_files)
            crud.update_harvest_status(
                db,
                harvest_status.harvest_id,
                HarvestStatus.FAILED,
                error_message=f"Some files failed to upload: {failed_files}"
            )
        else:
            crud.update_harvest_status(db, harvest_status.harvest_id,
                                       status=HarvestStatus.COMPLETED)
    return harvest_status


@app.post("/start_harvest", response_model=HarvestBase)
async def start_harvest(request: HarvestRequest,
                        db: Session = Depends(get_db)):
    logger.info(
        f"Received request to start harvest with data: {request}")

    params = {
        'verb': request.verb,
        'metadataPrefix': request.metadata_prefix,
    }

    if request.oai_set is not None:
        params['set'] = request.oai_set

    harvest_status = crud.create_harvest(db)

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            harvest_oai_pmh(request.oai_endpoint, temp_dir, params,
                            request.verb)

        except requests.exceptions.RequestException as e:
            error_message = f"Failed to retrieve data for harvest: {e}"
            logger.error(error_message)
            crud.update_harvest_status(db, harvest_status.harvest_id,
                                       HarvestStatus.FAILED,
                                       error_message=error_message)
            raise HTTPException(status_code=500, detail=error_message)

        except ET.ParseError as e:
            error_message = f"Error parsing XML response: {str(e)}"
            logger.error(error_message)
            crud.update_harvest_status(db, harvest_status.harvest_id,
                                       HarvestStatus.FAILED,
                                       error_message=error_message)
            raise HTTPException(status_code=500, detail=error_message)

        failed_files = upload_files_to_s3(s3client, temp_dir,
                                          request.bucket_name)
        if failed_files:
            crud.create_failed_files(db, harvest_status.harvest_id,
                                     failed_files)
            crud.update_harvest_status(
                db,
                harvest_status.harvest_id,
                HarvestStatus.FAILED,
                error_message=f"Some files failed to upload: {failed_files}"
            )
        else:
            crud.update_harvest_status(db, harvest_status.harvest_id,
                                       status=HarvestStatus.COMPLETED)
    logger.info('Returning harvest status.')
    return harvest_status
