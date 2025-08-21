import logging
import os
import requests
from abc import ABC, abstractmethod


LISS_ENDPOINT_URL = os.environ['LISS_ENDPOINT_URL']
LISS_ENDPOINT_USERNAME = os.environ['LISS_ENDPOINT_USERNAME']
LISS_ENDPOINT_KEY = os.environ['LISS_ENDPOINT_KEY']
VERIFY_SSL = os.environ.get('VERIFY_SSL', 'True').lower() == 'true'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HarvestClient(ABC):
    """

    """
    @abstractmethod
    def get_id_list(self, from_date: str) -> list[str]:
        pass

    @abstractmethod
    def fetch_metadata(self, dataset_id):
        pass


class LISSClient(HarvestClient):
    """ Retrieves id's of all exposed liss datasets."""

    def get_id_list(self, from_date: str):
        url = f"{LISS_ENDPOINT_URL}?from={from_date}"
        response = requests.get(url, auth=(LISS_ENDPOINT_USERNAME, LISS_ENDPOINT_KEY))
        json_data = response.json()

        return [item["id"] for item in json_data]

    def fetch_metadata(self, dataset_id):
        """
        """
        url = LISS_ENDPOINT_URL + f'?id={dataset_id}'
        try:
            return requests.get(
                url, auth=(LISS_ENDPOINT_USERNAME, LISS_ENDPOINT_KEY)).json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve data for id {dataset_id}: {e}")
