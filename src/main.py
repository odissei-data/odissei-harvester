import logging
import crud
import models

from sqlalchemy.orm import Session
from LISS_harvester import harvest_liss_metadata
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from S3Client import get_s3_client
from database import engine, SessionLocal
from harvester import harvest_metadata
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


@app.post("/start_liss_harvest_background", response_model=HarvestBase)
async def start_liss_harvest_background(request: LISSRequest,
                                        background_tasks: BackgroundTasks,
                                        db: Session = Depends(get_db)):
    logger.info(f"Received request to start LISS harvest with data: {request}")

    harvest_status = crud.create_harvest(db)
    background_tasks.add_task(harvest_liss_metadata, request, db,
                              harvest_status, s3client)

    return harvest_status


@app.post("/start_liss_harvest", response_model=HarvestBase)
async def start_liss_harvest(request: LISSRequest,
                             db: Session = Depends(get_db)):
    logger.info(f"Received request to start LISS harvest with data: {request}")
    harvest_status = crud.create_harvest(db)
    await harvest_liss_metadata(request, db, harvest_status, s3client)

    return harvest_status


@app.post("/start_harvest_background", response_model=HarvestBase)
async def start_harvest_background(request: HarvestRequest,
                                   background_tasks: BackgroundTasks,
                                   db: Session = Depends(get_db)):
    logger.info(f"Received request to start harvest with data: {request}")
    harvest_status = crud.create_harvest(db)
    background_tasks.add_task(harvest_metadata, request, db, harvest_status,
                              s3client)

    return harvest_status


@app.post("/start_harvest", response_model=HarvestBase)
async def start_harvest(request: HarvestRequest,
                        db: Session = Depends(get_db)):
    logger.info(f"Received request to start harvest with data: {request}")
    harvest_status = crud.create_harvest(db)
    harvest_metadata(request, db, harvest_status, s3client)

    return harvest_status
