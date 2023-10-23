# import os
# from datetime import datetime
# from unittest.mock import patch
#
# import moto as moto
# from starlette.testclient import TestClient
# from models import Harvest, HarvestStatus
# from server import create_server
#
# api_key = os.environ.get("API_KEY")
#
#
# class DummyHarvestRepo:
#     def create_harvest(self):
#         return Harvest(id=1, harvest_id=1, start_time=datetime.now(),
#                        status=HarvestStatus.PENDING)
#
#     def update_harvest_failed(self, harvest_id, error_message):
#         return Harvest(id=1, harvest_id=harvest_id, start_time=datetime.now(),
#                        status=HarvestStatus.FAILED,
#                        error_message=error_message)
#
#     def update_harvest_success(self, harvest_id):
#         return Harvest(id=1, harvest_id=harvest_id, start_time=datetime.now(),
#                        status=HarvestStatus.COMPLETED)
#
#     def get_harvest_status(self, harvest_id):
#         return Harvest(id=1, harvest_id=harvest_id, start_time=datetime.now(),
#                        status=HarvestStatus.COMPLETED)
#
#
# headers = {"X-API-Key": api_key}
# s3client = moto.mock_s3()
# repo = DummyHarvestRepo()
# server = create_server(s3client, repository=repo)
# test_client = TestClient(app=server)
#
#
# def test_start_liss_harvest_background_endpoint():
#     with patch('S3Client.create_bucket_if_not_exists', return_value=None):
#         liss_request_data = {
#             "bucket_name": "liss-harvest-test"
#         }
#         response = test_client.post("/start_liss_harvest_background",
#                                     json=liss_request_data, headers=headers)
#         assert response.status_code == 200
#         assert "harvest_id" in response.json()
#
#
# def test_start_harvest_background_endpoint():
#     with patch('S3Client.create_bucket_if_not_exists', return_value=None):
#         harvest_request_data = {
#             "metadata_prefix": "oai_dc",
#             "oai_set": "Groningen_Social_Sciences",
#             "oai_endpoint": "https://dataverse.nl/oai",
#             "bucket_name": "groningen-identifier-test",
#             "verb": "ListIdentifiers"
#         }
#         response = test_client.post("/start_harvest_background",
#                                     json=harvest_request_data,
#                                     headers=headers)
#         assert response.status_code == 200
#         assert "harvest_id" in response.json()
#
#
# def test_start_harvest_endpoint():
#     with patch('S3Client.create_bucket_if_not_exists', return_value=None):
#         harvest_request_data = {
#             "metadata_prefix": "oai_dc",
#             "oai_set": "Groningen_Social_Sciences",
#             "oai_endpoint": "https://dataverse.nl/oai",
#             "bucket_name": "groningen-identifier-test",
#             "verb": "ListIdentifiers"
#         }
#         response = test_client.post("/start_harvest",
#                                     json=harvest_request_data,
#                                     headers=headers)
#         assert response.status_code == 200
#         assert "harvest_id" in response.json()
#
#
# def test_get_harvest_status_endpoint():
#     # Create a harvest_id for testing (replace with an actual valid harvest_id)
#     test_harvest_id = 1
#
#     response = test_client.get(f"/harvest_status/{test_harvest_id}")
#     assert response.status_code == 200
#
#     # Assuming your API returns the harvest status for the given harvest_id
#     assert "harvest_id" in response.json()
