# /app_old/utils/http_callback.py

import requests
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_callback(job_number: str, callback_url: str, data: list):
    """
    Function to send a callback to a FastAPI callback URL.

    :param job_number: The job number for tracking the request
    :param callback_url: The callback URL to send the request to
    :param data: The data to send in the POST request
    """

    try:
        print("job_number: ", job_number)
        logger.info(f"job_number: {job_number}")
        print("callback_url: ", callback_url)
        logger.info(f"callback_url: {callback_url}")
        print("type(data)1: ", type(data))
        # data =json.dumps(data)
        print("type(data)2: ", type(data))
        print("data: ", data)
        logger.info(f"data: {data}")
        full_callback_url = f"{callback_url}?job_number={job_number}"
        print("callback_url2: ", full_callback_url)
        logger.info(f"callback_url2: {full_callback_url}")
        headers = {'Content-Type': 'application/json'}
        response = requests.post(full_callback_url, json=data, headers=headers, allow_redirects=True)
        print("response.json(): ", response.json())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send callback: {e}")
        return None
