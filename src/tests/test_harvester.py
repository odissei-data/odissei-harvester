import os
from datetime import datetime
from unittest.mock import patch

import moto as moto
from starlette.testclient import TestClient
from models import Harvest, HarvestStatus
from server import create_server

api_key = os.environ.get("API_KEY")


class DummyHarvestRepo:
    def create_harvest(self):
        return Harvest(id=1, harvest_id=1, start_time=datetime.now(),
                       status=HarvestStatus.PENDING)

    def update_harvest_failed(self, harvest_id, error_message):
        return Harvest(id=1, harvest_id=harvest_id, start_time=datetime.now(),
                       status=HarvestStatus.FAILED,
                       error_message=error_message)

    def update_harvest_success(self, harvest_id):
        return Harvest(id=1, harvest_id=harvest_id, start_time=datetime.now(),
                       status=HarvestStatus.COMPLETED)

    def get_harvest_status(self, harvest_id):
        return Harvest(id=1, harvest_id=harvest_id, start_time=datetime.now(),
                       status=HarvestStatus.COMPLETED)


headers = {"X-API-Key": api_key}
s3client = moto.mock_s3()
repo = DummyHarvestRepo()
server = create_server(s3client, repository=repo)
test_client = TestClient(app=server)


# TODO: still having trouble with testing the harvesters that use repo
# TODO: because database.py starts the db even in test.


