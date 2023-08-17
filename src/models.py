import enum

from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey

from database import Base


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
    failed_files = relationship('FailedFile', back_populates='harvest')


class FailedFile(Base):
    __tablename__ = 'failed_files'

    id = Column(Integer, primary_key=True)
    harvest_id = Column(Integer, ForeignKey('harvests.id'), nullable=False)
    filename = Column(String, nullable=False)
    harvest = relationship('Harvest', back_populates='failed_files')
