from fastapi import FastAPI

from api import router


def create_server(s3client, repository):
    server = FastAPI()
    server.include_router(router)
    server.repository = repository
    server.s3client = s3client
    return server
