import os

from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status

API_KEY = os.environ['API_KEY']
api_keys = [API_KEY]
api_key_header = APIKeyHeader(name="X-API-Key")


def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header in api_keys:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )