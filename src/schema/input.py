from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class OAIHarvestRequest(BaseModel):
    metadata_prefix: str = Field(example="oai_dc")
    oai_endpoint: str = Field(example="https://dataverse.nl/oai")
    bucket_name: str = Field(example="dataverse-nl")
    verb: str = Field(example="ListIdentifiers")
    oai_set: Optional[str] = Field(None, example="Groningen_Social_Sciences")
    timestamp: Optional[datetime] = Field(None, example="2024-05-30 14:30:00")

class HarvestRequest(BaseModel):
    bucket_name: str = Field("example-bucket-name")
    timestamp: Optional[datetime] = Field(None, example="2004-12-10 17:30:00")
