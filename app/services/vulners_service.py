"""Service to interact with Vulners API."""

from app.constants import Constants as CONST
import datetime as datetime
import requests
import json

from app.logger import setup_logger

import datetime as datetime
import time

logger = setup_logger(__name__)


class VulnersService():
    """Service class to interact with Vulners API."""

    def __init__(self):
        """Initialize the VulnersService."""
        self.base_url = f"{CONST.SERVER}{CONST.API_VERSION}"

    def get_vulnerability(self) -> dict:
        """To fetch vulnerability details from Vulners API for
        a given package as part of payload.
        Ex:{
            "version": "2.3.3",
            "package": {
                "name": "pandas",
                "ecosystem": "PyPI"
            }
         }
        args:
            payload (dict): The payload containing package details.
        returns:
            dict: The response from the Vulners API.
        """
        url = f"{self.base_url}{CONST.QUERY_PATH}"
        payload = {
            "version": "2.3.3",
            "package": {
                "name": "pandas",
                "ecosystem": "PyPI"
            }
         }
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            logger.info(f"Successfully fetched data from Vulners API.{response.json()}")
            return response.json()

        else:
            return {"error": f"Failed to fetch data for", "status_code": response.status_code}