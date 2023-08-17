import json
import os
import requests
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

LISS_ENDPOINT_URL = os.environ['LISS_ENDPOINT_URL']
LISS_ENDPOINT_USERNAME = os.environ['LISS_ENDPOINT_USERNAME']
LISS_ENDPOINT_KEY = os.environ['LISS_ENDPOINT_KEY']


def get_liss_id_list():
    """ Retrieves id's of all exposed liss datasets.

    :return:
    """
    response = requests.get(LISS_ENDPOINT_URL, auth=(
        LISS_ENDPOINT_USERNAME, LISS_ENDPOINT_KEY))
    response.raise_for_status()
    json_data = response.json()

    return [item["id"] for item in json_data]


def get_metadata(liss_id):
    """

    :param liss_id:
    :return:
    """
    url = LISS_ENDPOINT_URL + f'?id={liss_id}'
    try:
        return requests.get(
            url, auth=(LISS_ENDPOINT_USERNAME, LISS_ENDPOINT_KEY)).json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to retrieve data for id {liss_id}: {e}")


def save_metadata(liss_id, data, temp_dir):
    file_name = f"{liss_id}.json"
    output_file = os.path.join(temp_dir,
                               f"record_{file_name}.xml")
    with open(output_file, "w") as f:
        json.dump(data, f)
    logger.info(f"Data for id {liss_id} saved to {file_name}")
