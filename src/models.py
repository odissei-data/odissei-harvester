import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class HarvestStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Harvest(Base):
    __tablename__ = 'harvests'

    id = Column(Integer, primary_key=True)
    harvest_id = Column(String, unique=True, nullable=False)
    status = Column(Enum(HarvestStatus), nullable=False,
                    default=HarvestStatus.PENDING)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    error_message = Column(String)
