import uuid

from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db
from models import Harvest, HarvestStatus


class HarvestRepository:

    def __init__(self) -> None:
        self.session: Session = get_db().__next__()

    def create_harvest(self):
        harvest_id = str(uuid.uuid4())
        new_harvest = Harvest(
            harvest_id=harvest_id, start_time=datetime.now(), error_message=""
        )
        self.session.add(new_harvest)

        self.session.commit()

        self.session.refresh(new_harvest)
        
        return new_harvest

    def update_harvest_failed(self, harvest_id, error_message):
        harvest = self.session.query(Harvest).filter_by(harvest_id=harvest_id).first()
        harvest.status = HarvestStatus.FAILED
        harvest.end_time = datetime.now()
        harvest.error_message = error_message
        self.session.commit()

    def update_harvest_success(self, harvest_id):
        harvest = self.session.query(Harvest).filter_by(harvest_id=harvest_id).first()
        harvest.status = HarvestStatus.COMPLETED
        harvest.end_time = datetime.now()
        self.session.commit()

    def get_harvest_status(self, harvest_id):
        return self.session.query(Harvest).filter_by(harvest_id=harvest_id).first()
