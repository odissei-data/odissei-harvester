import json
import os
import logging
import requests

import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def harvest_oai_pmh(endpoint_url, output_dir, params, verb):
    try:
        res = requests.get(endpoint_url, params=params)
        res.raise_for_status()  # Raise an exception if the request fails

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
            res.raise_for_status()  # Raise an exception if the request fails

    except requests.exceptions.RequestException as e:
        logger.error(f"Error during GET request to OAI-PMH endpoint: {str(e)}")
    except ET.ParseError as e:
        logger.error(f"Error parsing XML response: {str(e)}")


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
        ).text.strip()

        output_file = os.path.join(output_dir,
                                   f"record_{file_name}.xml")
        with open(output_file, 'wb') as f:
            f.write(ET.tostring(record, encoding='utf-8'))
        print(f"Record {file_name} saved")


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
