from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from models import HarvestStatus


class HarvestBase(BaseModel):
    id: int
    harvest_id: str
    status: HarvestStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        orm_mode = True
