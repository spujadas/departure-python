"""
API for Nederlandse Spoorwegen
"""

import json
import os
import logging

import requests

from . import commons

logger = logging.getLogger(__name__)


def api_request(url: str, payload: dict) -> str:
    commons.check_env_vars()

    try:
        response = requests.get(
            url,
            params=payload,
            timeout=15,
            headers={"Ocp-Apim-Subscription-Key": os.environ["NS_API_KEY"]},
        )
    except requests.exceptions.Timeout:
        logger.warning("NS API HTTP request timed out")
        return None
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("NS API HTTP request error: %s", str(e))
        return None

    # process response
    if response.status_code == 200:
        return json.loads(response.content.decode("utf-8"))

    logger.warning("NS API request failed, HTTP response: %s", response.status_code)
    return None


def departures(station_code):
    url = "https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/departures"
    payload = {"station": station_code, "lang": "en"}
    return api_request(url, payload)


def journey(train_number):
    url = "https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/journey"
    payload = {"train": train_number, "lang": "en"}
    return api_request(url, payload)
