import pytest
import json
import os
from unittest.mock import AsyncMock
from harvester import fetch_and_save_metadata, save_metadata

def test_save_metadata(tmp_path):
    # Mock dependencies
    dataset_id = "test_id"
    dataset_metadata = {"data": "metadata"}
    temp_dir = tmp_path

    # Run the function
    save_metadata(dataset_id, dataset_metadata, temp_dir)

    # Assertions
    output_file = os.path.join(temp_dir, f"{dataset_id}.json")
    assert os.path.exists(output_file)
    with open(output_file, "r") as f:
        data = json.load(f)
    assert data == dataset_metadata

@pytest.mark.asyncio
async def test_fetch_and_save_metadata_with_exception():
    # Mock dependencies
    mock_harvest_client = AsyncMock()
    mock_harvest_client.fetch_metadata = AsyncMock(side_effect=Exception("Fetch error"))
    temp_dir = "/tmp/test_dir"

    # Run the function and assert exception
    with pytest.raises(Exception):
        await fetch_and_save_metadata("test_id", temp_dir, mock_harvest_client)

    # Assertions
    mock_harvest_client.fetch_metadata.assert_called_once_with("test_id")
