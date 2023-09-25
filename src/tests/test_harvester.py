from datetime import datetime

import moto as moto
import pytest
from unittest.mock import Mock, patch

from starlette.testclient import TestClient

from harvester import extract_records, extract_identifiers, harvest_oai_pmh
from models import Harvest
from server import create_server


class DummyHarvestRepo:
    def create_harvest(self):
        return ''

    def update_harvest_failed(self):
        pass

    def update_harvest_success(self):
        pass

    def get_harvest_status(self):
        return Harvest(harvest_id=1, start_time=datetime.now())


s3client = moto.mock_s3()
repo = DummyHarvestRepo()
server = create_server(s3client, repository=repo)
test_client = TestClient(app=server)


def test_version_endpoint(test_client):
    response = test_client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": "your_version_here"}


def test_start_liss_harvest_background_endpoint(test_client):
    # Create a sample LISSRequest
    liss_request_data = {
        "param1": "value1",
        "param2": "value2",
        # Add other required parameters
    }

    response = test_client.post("/start_liss_harvest_background",
                                json=liss_request_data)
    assert response.status_code == 200

    # Assuming your API returns the created harvest status
    assert "harvest_id" in response.json()


def test_start_liss_harvest_endpoint():
    # Create a sample LISSRequest
    liss_request_data = {
        "param1": "value1",
        "param2": "value2",
        # Add other required parameters
    }

    response = test_client.post("/start_liss_harvest", json=liss_request_data)
    assert response.status_code == 200

    # Assuming your API returns the created harvest status
    assert "harvest_id" in response.json()


def test_start_harvest_background_endpoint():
    # Create a sample HarvestRequest
    harvest_request_data = {
        "param1": "value1",
        "param2": "value2",
        # Add other required parameters
    }

    response = test_client.post("/start_harvest_background",
                                json=harvest_request_data)
    assert response.status_code == 200

    # Assuming your API returns the created harvest status
    assert "harvest_id" in response.json()


def test_start_harvest_endpoint():
    # Create a sample HarvestRequest
    harvest_request_data = {
        "param1": "value1",
        "param2": "value2",
        # Add other required parameters
    }

    response = test_client.post("/start_harvest", json=harvest_request_data)
    assert response.status_code == 200

    # Assuming your API returns the created harvest status
    assert "harvest_id" in response.json()


def test_get_harvest_status_endpoint():
    # Create a harvest_id for testing (replace with an actual valid harvest_id)
    test_harvest_id = 1

    response = test_client.get(f"/harvest_status/{test_harvest_id}")
    assert response.status_code == 200

    # Assuming your API returns the harvest status for the given harvest_id
    assert "harvest_id" in response.json()


def test_get_harvest_status_endpoint_invalid_id():
    # Create an invalid harvest_id for testing (replace with an invalid harvest_id)
    invalid_harvest_id = "invalid_id"

    response = test_client.get(f"/harvest_status/{invalid_harvest_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Harvest not found"}
