from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class OAIHarvestRequest(BaseModel):
    metadata_prefix: str = Field(default="oai_dc", json_schema_extra={"example": "oai_dc"})
    oai_endpoint: str = Field(default="https://dataverse.nl/oai", json_schema_extra={"example": "https://dataverse.nl/oai"})
    bucket_name: str = Field(default="dataverse-nl", json_schema_extra={"example": "dataverse-nl"})
    verb: str = Field(default="ListIdentifiers", json_schema_extra={"example": "ListIdentifiers"})
    oai_set: Optional[str] = Field(default=None, json_schema_extra={"example": "Groningen_Social_Sciences"})
    timestamp: Optional[datetime] = Field(default=None, json_schema_extra={"example": "2024-05-30 14:30:00"})


class HarvestRequest(BaseModel):
    bucket_name: str = Field(default="example-bucket-name", json_schema_extra={"example": "example-bucket-name"})
    timestamp: Optional[datetime] = Field(default=None, json_schema_extra={"example": "2004-12-10 17:30:00"})
