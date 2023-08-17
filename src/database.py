import datetime
import enum
import os

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

POSTGRES_DB_URL = os.environ['POSTGRES_DB_URL']


class HarvestStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Harvest(Base):
    __tablename__ = 'harvests'

    id = Column(Integer, primary_key=True)
    harvest_id = Column(String, unique=True, nullable=False)
    status = Column(Enum(HarvestStatus), default=HarvestStatus.PENDING)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    error_message = Column(String)


def setup_database(db_url):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def create_harvest(session, harvest_id):
    new_harvest = Harvest(harvest_id=harvest_id)
    session.add(new_harvest)
    session.commit()


def update_harvest_status(session, harvest_id, status, error_message=None):
    harvest = session.query(Harvest).filter_by(harvest_id=harvest_id).first()
    if harvest:
        harvest.status = status
        if status == HarvestStatus.COMPLETED or status == HarvestStatus.FAILED:
            harvest.end_time = datetime.datetime.now()
        if error_message:
            harvest.error_message = error_message
        session.commit()


def get_harvest_status(session, harvest_id):
    harvest = session.query(Harvest).filter_by(harvest_id=harvest_id).first()
    if harvest:
        return {
            "harvest_id": harvest.harvest_id,
            "status": harvest.status.value,
            "start_time": harvest.start_time,
            "end_time": harvest.end_time,
            "error_message": harvest.error_message
        }
    return None


def create_database_session():
    engine = create_engine(POSTGRES_DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
