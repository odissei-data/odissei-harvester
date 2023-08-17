import uuid

from datetime import datetime
from models import Harvest, HarvestStatus, FailedFile


def create_harvest(session):
    harvest_id = str(uuid.uuid4())
    new_harvest = Harvest(harvest_id=harvest_id, start_time=datetime.now())
    session.add(new_harvest)
    session.commit()
    session.refresh(new_harvest)
    return new_harvest


def update_harvest_status(session, harvest_id, status, error_message=None):
    harvest = session.query(Harvest).filter_by(harvest_id=harvest_id).first()
    if harvest:
        harvest.status = status
        if status == HarvestStatus.COMPLETED or status == HarvestStatus.FAILED:
            harvest.end_time = datetime.now()
        if error_message:
            harvest.error_message = error_message
        session.commit()


def get_harvest_status(session, harvest_id):
    return session.query(Harvest).filter_by(harvest_id=harvest_id).first()


def create_failed_files(session, harvest_id, filenames):
    for failed_filename in filenames:
        failed_file = FailedFile(harvest_id=harvest_id,
                                 filename=failed_filename)
        session.add(failed_file)
