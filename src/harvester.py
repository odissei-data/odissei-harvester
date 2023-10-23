import json
import os
import logging
import tempfile

import requests

import xml.etree.ElementTree as ET

from botocore.client import BaseClient
from fastapi import HTTPException
from S3Client import upload_files_to_s3
from models import Harvest
from schema.input import HarvestRequest

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def harvest_metadata(request: HarvestRequest, harvest_repo,
                     harvest_status: Harvest, s3client: BaseClient):
    params = {
        'verb': request.verb,
        'metadataPrefix': request.metadata_prefix,
    }

    if request.oai_set is not None:
        params['set'] = request.oai_set

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            harvest_oai_pmh(request.oai_endpoint, temp_dir, params,
                            request.verb)

        except requests.exceptions.RequestException as e:
            error_message = f"Failed to retrieve data for harvest: {e}"
            logger.error(error_message)
            harvest_repo.update_harvest_failed(harvest_status.harvest_id,
                                               error_message=error_message)
            raise HTTPException(status_code=500, detail=error_message)

        except ET.ParseError as e:
            error_message = f"Error parsing XML response: {str(e)}"
            logger.error(error_message)
            harvest_repo.update_harvest_failed(harvest_status.harvest_id,
                                               error_message=error_message)
            raise HTTPException(status_code=500, detail=error_message)

        upload_files_to_s3(s3client, temp_dir, request.bucket_name)
        harvest_repo.update_harvest_success(harvest_status.harvest_id)
        logger.info(f'Successfully harvested: {harvest_status.harvest_id}')


def harvest_oai_pmh(endpoint_url, output_dir, params, verb):
    try:
        res = requests.get(endpoint_url, params=params)
        res.raise_for_status()
        logger.info('Starting harvest')
        while res.status_code == 200:
            # Parse the XML response
            root = ET.fromstring(res.content)
            # Extract metadata records from the response
            if verb == 'ListRecords':
                extract_records(root, output_dir)
            if verb == 'ListIdentifiers':
                extract_identifiers(root, output_dir)

            # Check if there are more records to be fetched
            resumption_token = root.find(
                './/{http://www.openarchives.org/OAI/2.0/}resumptionToken')
            if resumption_token is None:
                break

            res = requests.get(endpoint_url, params={
                'verb': verb,
                'resumptionToken': resumption_token.text
            })
            res.raise_for_status()

    except requests.exceptions.RequestException as e:
        logger.error(f"Error during GET request to OAI-PMH endpoint: {str(e)}")
    logger.info('Harvest completed.')


def extract_records(root, output_dir):
    for _, record in enumerate(root.findall(
            './/{http://www.openarchives.org/OAI/2.0/}ListRecords/'
            '{http://www.openarchives.org/OAI/2.0/}record')):

        # Find the status of the record.
        status = record.find(
            './/{http://www.openarchives.org/OAI/2.0/}header'
        ).get('status')
        if status == 'deleted':
            continue

        file_name = record.find(
            './/{http://www.openarchives.org/OAI/2.0/}header/'
            '{http://www.openarchives.org/OAI/2.0/}identifier'
        ).text.strip().replace('/', '_')

        output_file = os.path.join(output_dir,
                                   f"record_{file_name}.xml")
        logger.info(f'File harvested: {file_name}')
        with open(output_file, 'wb') as f:
            f.write(ET.tostring(record, encoding='utf-8'))


def extract_identifiers(root, output_dir):
    identifiers_file_path = os.path.join(output_dir, f"identifiers.json")

    # If the identifiers file already exists, load its contents as JSON.
    if os.path.exists(identifiers_file_path):
        with open(identifiers_file_path, 'r',
                  encoding='utf-8') as identifiers_file:
            existing_data = json.load(identifiers_file)
    else:
        # Otherwise, initialize an empty JSON object.
        existing_data = {"pids": []}

    for _, record in enumerate(root.findall(
            './/{http://www.openarchives.org/OAI/2.0/}ListIdentifiers/'
            '{http://www.openarchives.org/OAI/2.0/}header')):

        if record.get('status') == 'deleted':
            continue

        identifier = record.find(
            './/{http://www.openarchives.org/OAI/2.0/}identifier').text.strip()
        existing_data["pids"].append(identifier)

    # Write the updated JSON object to the file
    with open(identifiers_file_path, 'w',
              encoding='utf-8') as identifiers_file:
        json.dump(existing_data, identifiers_file)
