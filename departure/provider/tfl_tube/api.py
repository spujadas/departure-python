import json
import os
import logging
from typing import List

import requests

from . import commons

logger = logging.getLogger(__name__)


def unified_api_request(base_url: str, base_queries: List[str] = None):
    # check environment variables
    commons.check_env_vars()

    # build URL and send request
    url = f'{base_url}?app_key={os.environ["TFL_APP_KEY"]}'
    if base_queries:
        url = f"{url}&{'&'.join(base_queries)}"

    try:
        response = requests.get(url, timeout=15)
    except requests.exceptions.Timeout:
        logger.warning("TfL unified API HTTP request timed out")
        return None
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("TfL unified API HTTP request error: %s", str(e))
        return None

    # process response
    if response.status_code == 200:
        return json.loads(response.content.decode("utf-8"))

    return None


def line_stoppoints(line_id):
    base_url = f"https://api.tfl.gov.uk/Line/{line_id}/StopPoints"
    stoppoints = unified_api_request(base_url)

    return stoppoints


def line_arrivals(
    line_ids: List[str], station_id: str = ""  # default: all stations on lines
):
    base_url = f"https://api.tfl.gov.uk/Line/{','.join(line_ids)}/Arrivals/{station_id}"
    return unified_api_request(base_url)


def tube_arrivals(count: int = 2):
    base_url = "https://api.tfl.gov.uk/Mode/tube/Arrivals"
    base_queries = [f"count={count}"]

    return unified_api_request(base_url, base_queries)
