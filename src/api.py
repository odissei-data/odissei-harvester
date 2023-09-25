import logging

from starlette.requests import Request
from LISS_harvester import harvest_liss_metadata
from fastapi import HTTPException, BackgroundTasks, APIRouter, Depends
from auth import get_api_key
from harvester import harvest_metadata
from schema.harvest import HarvestBase
from schema.input import HarvestRequest, LISSRequest
from version import get_version

router = APIRouter()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@router.get("/version")
async def info():
    result = get_version()
    return {"version": result}


@router.get("/harvest_status/{harvest_id}", response_model=HarvestBase)
async def get_status(request: Request, harvest_id: str):
    harvest_repo = request.app.repository
    harvest_status = harvest_repo.get_harvest_status(harvest_id)
    if harvest_status is None:
        raise HTTPException(status_code=404, detail="Harvest not found")
    return harvest_status


@router.post("/start_liss_harvest_background", response_model=HarvestBase,
             dependencies=[Depends(get_api_key)])
async def start_liss_harvest_background(request: Request,
                                        liss_request: LISSRequest,
                                        background_tasks: BackgroundTasks):
    logger.info(f"Starting LISS harvest with data: {liss_request}")
    harvest_repo = request.app.repository
    s3client = request.app.s3client
    harvest_status = harvest_repo.create_harvest()

    background_tasks.add_task(harvest_liss_metadata, liss_request,
                              harvest_repo,
                              harvest_status, s3client)

    return harvest_status


@router.post("/start_liss_harvest", response_model=HarvestBase,
             dependencies=[Depends(get_api_key)])
async def start_liss_harvest(request: Request, liss_request: LISSRequest):
    logger.info(f"Starting LISS harvest with data: {liss_request}")
    harvest_repo = request.app.repository
    s3client = request.app.s3client

    harvest_status = harvest_repo.create_harvest()
    await harvest_liss_metadata(liss_request, harvest_repo, harvest_status,
                                s3client)

    return harvest_status


@router.post("/start_harvest_background", response_model=HarvestBase,
             dependencies=[Depends(get_api_key)])
async def start_harvest_background(request: Request,
                                   harvest_request: HarvestRequest,
                                   background_tasks: BackgroundTasks):
    logger.info(f"Starting harvest with data: {harvest_request}")
    harvest_repo = request.app.repository
    s3client = request.app.s3client

    harvest_status = harvest_repo.create_harvest()
    background_tasks.add_task(harvest_metadata, harvest_request, harvest_repo,
                              harvest_status, s3client)

    return harvest_status


@router.post("/start_harvest", response_model=HarvestBase,
             dependencies=[Depends(get_api_key)])
async def start_harvest(request: Request, harvest_request: HarvestRequest):
    logger.info(f"Starting harvest with data: {harvest_request}")
    harvest_repo = request.app.repository
    s3client = request.app.s3client

    harvest_status = harvest_repo.create_harvest()
    harvest_metadata(harvest_request, harvest_repo, harvest_status, s3client)

    return harvest_status
