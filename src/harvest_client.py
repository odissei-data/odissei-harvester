from datetime import datetime
import ckanapi
import logging
import os
import requests
from abc import ABC, abstractmethod


CID_ENDPOINT_URL = os.environ['CID_ENDPOINT_URL']
CID_CKAN_ENDPOINT_URL = CID_ENDPOINT_URL.replace('/api/3/action/', '')
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
    def get_id_list(self, from_date: str):
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


class CIDClient(HarvestClient):

    def get_id_list(self, from_date: str):
        if from_date:
            result = []
            if isinstance(from_date, datetime):
                from_date = from_date.strftime("%Y-%m-%d")
            date_obj = datetime.strptime(from_date, "%Y-%m-%d")

            # Format the datetime object to the desired format
            formatted_date = date_obj.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            #https://test.data.individualdevelopment.nl/api/3/action/package_search?q=metadata_modified:[2024-07-01T00:00:00.000Z+TO+NOW]+&sort=score+desc,+metadata_modified+desc
            session = requests.Session()
            session.verify = VERIFY_SSL
            ckan = ckanapi.RemoteCKAN(CID_CKAN_ENDPOINT_URL, get_only=True, session=session)
            start = 0
            rows = 100  # Number of datasets to retrieve per request
            while True:
                # Perform the package_search action with pagination
                query = f'metadata_modified:[{formatted_date} TO NOW]'
                try:
                    response = ckan.action.package_search(q=query, sort='metadata_modified desc', start=start, rows=rows)
                except ckanapi.errors.CKANAPIError as e:
                    logger.error(f"Failed to retrieve data: {e}")
                    return result

                # Print the results
                for dataset in response['results']:
                    # print(dataset['title'], dataset['metadata_modified'])
                    result.append(dataset['name'])
                # Check if there are more datasets to retrieve
                if len(response['results']) < rows:
                    break

                # Update the start parameter for the next batch
                start += rows
            return result
        else:
            response = requests.get(CID_ENDPOINT_URL + 'package_list', verify=VERIFY_SSL)
            response.raise_for_status()
            return response.json()['result']

    def fetch_metadata(self, dataset_id):
        url = f'{CID_ENDPOINT_URL}package_show?id={dataset_id}'
        try:
            return requests.get(url).json()['result']
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve dat for id {dataset_id}: {e}")
