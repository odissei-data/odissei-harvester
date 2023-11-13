from typing import Optional

from pydantic import BaseModel, Field


class OAIHarvestRequest(BaseModel):
    metadata_prefix: str = Field(example="oai_dc")
    oai_set: Optional[str] = Field(None, example="Groningen_Social_Sciences")
    oai_endpoint: str = Field(example="https://dataverse.nl/oai")
    bucket_name: str = Field(example="dataverse-nl")
    verb: str = Field(example="ListIdentifiers")


class HarvestRequest(BaseModel):
    bucket_name: str = Field("example-bucket-name")
