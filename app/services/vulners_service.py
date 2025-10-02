"""Service to interact with Vulners API."""

from app.constants import Constants as CONST
from app.logger import setup_logger

import datetime as datetime
import requests
import datetime as datetime


logger = setup_logger(__name__)


class VulnersService():
    """Service class to interact with Vulners API."""

    def __init__(self):
        """Initialize the VulnersService."""
        self.base_url = f"{CONST.SERVER}{CONST.API_VERSION}"

    def get_vulnerability(self, project_name, project_description) -> dict:
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
            project_name (str): Name of the project.
            project_description (str): Description of the project.

        returns:
            dict: The response from the Vulners API.
        """
        logger.info("START: Fetching vulnerability details from Vulners API.")

        url = f"{self.base_url}{CONST.QUERY_PATH}"

        #TBD Hardcoded now, later on from request
        #TBD To handle incoming arguments
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
            result = response.json()

        else:
            result =  {"error": f"Failed to fetch data for", "status_code": response.status_code}

        logger.info("END: Fetching vulnerability details from Vulners API.")

        return result