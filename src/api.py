import logging

from starlette.requests import Request
from harvester import harvest_metadata
from fastapi import HTTPException, BackgroundTasks, APIRouter, Depends
from auth import get_api_key
from OAI_harvester import oai_harvest_metadata
from harvest_client import LISSClient
from schema.harvest import HarvestBase
from schema.input import OAIHarvestRequest, HarvestRequest
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
                                        liss_request: HarvestRequest,
                                        background_tasks: BackgroundTasks):
    logger.info(f"Starting LISS harvest with data: {liss_request}")
    harvest_repo = request.app.repository
    harvest_client = LISSClient()
    s3client = request.app.s3client
    harvest_status = harvest_repo.create_harvest()

    background_tasks.add_task(harvest_metadata, liss_request,
                              harvest_client,
                              harvest_repo,
                              harvest_status, s3client)

    return harvest_status


@router.post("/start_liss_harvest", response_model=HarvestBase,
             dependencies=[Depends(get_api_key)])
async def start_liss_harvest(request: Request, liss_request: HarvestRequest):
    logger.info(f"Starting LISS harvest with data: {liss_request}")
    harvest_repo = request.app.repository
    s3client = request.app.s3client
    harvest_client = LISSClient()

    harvest_status = harvest_repo.create_harvest()
    await harvest_metadata(liss_request, harvest_client, harvest_repo,
                           harvest_status, s3client)

    return harvest_status


@router.post("/start_harvest_background", response_model=HarvestBase,
             dependencies=[Depends(get_api_key)])
async def start_harvest_background(request: Request,
                                   harvest_request: OAIHarvestRequest,
                                   background_tasks: BackgroundTasks):
    logger.info(f"Starting harvest with data: {harvest_request}")
    harvest_repo = request.app.repository
    s3client = request.app.s3client

    harvest_status = harvest_repo.create_harvest()
    background_tasks.add_task(oai_harvest_metadata, harvest_request,
                              harvest_repo,
                              harvest_status, s3client)

    return harvest_status


@router.post("/start_harvest", response_model=HarvestBase,
             dependencies=[Depends(get_api_key)])
async def start_harvest(request: Request, harvest_request: OAIHarvestRequest):
    logger.info(f"Starting harvest with data: {harvest_request}")
    harvest_repo = request.app.repository
    s3client = request.app.s3client

    harvest_status = harvest_repo.create_harvest()
    oai_harvest_metadata(harvest_request, harvest_repo, harvest_status,
                         s3client)

    return harvest_status
