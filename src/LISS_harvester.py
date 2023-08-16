import json
import os
import requests

username = "dans"
password = "qwWWjwde3hSwd"


def get_liss_id_list():
    url = "https://www.oai-pmh.centerdata.nl/lissdata_json/"
    try:
        response = requests.get(url, auth=(username, password))
        response.raise_for_status()
        json_data = response.json()

        return [item["id"] for item in json_data]

    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")


def get_and_save_data(liss_id, base_url, temp_dir):
    url = base_url.format(liss_id)
    response = requests.get(url, auth=(username, password))

    if response.status_code == 200:
        file_name = f"{liss_id}.json"
        output_file = os.path.join(temp_dir,
                                   f"record_{file_name}.xml")
        with open(output_file, "w") as f:
            json.dump(response.json(), f)
        print(f"Data for id {liss_id} saved to {file_name}")
    else:
        print(
            f"Failed to retrieve data for id {liss_id}. "
            f"Status code: {response.status_code}")