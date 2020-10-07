import xml.etree.ElementTree as ET
import os
import logging

import requests

from . import commons

logger = logging.getLogger(__name__)


def api_request(url: str):
    commons.check_env_vars()

    try:
        response = requests.get(
            url,
            timeout=15,
            auth=(os.environ["TRANSILIEN_USER"], os.environ["TRANSILIEN_PASSWORD"]),
        )
    except requests.exceptions.Timeout:
        logger.warning("Transilien API HTTP request timed out")
        return None
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("Transilien API HTTP request error: %s", str(e))
        return None

    # process response
    if response.status_code == 200:
        return ET.fromstring(response.content.decode("utf-8"))

    return None


def departures(station_id):
    url = f"https://api.transilien.com/gare/{station_id}/depart/"
    return api_request(url)
