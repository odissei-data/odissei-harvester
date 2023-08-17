from datetime import datetime
from pydantic import BaseModel

from models import HarvestStatus


class HarvestBase(BaseModel):
    id: int
    harvest_id: str
    status: HarvestStatus
    start_time: datetime = None
    end_time: datetime = None
    error_message: str = None

    class Config:
        orm_mode = True
