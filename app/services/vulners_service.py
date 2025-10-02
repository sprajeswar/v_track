"""Service to interact with Vulners API."""

from fastapi import HTTPException, UploadFile
from http import HTTPStatus

from app.constants import Constants as CONST
from app.logger import setup_logger
from app.config import Config

import datetime as datetime
import requests
import json


logger = setup_logger(__name__)


class VulnersService():
    """Service class to interact with Vulners API."""

    def __init__(self):
        """Initialize the VulnersService."""
        self.base_url = f"{CONST.SERVER}{CONST.API_VERSION}"
        self.projects = {}

    def create_project(self, project_name: str, project_description: str,
                          requirements_file: UploadFile) -> dict:
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

        qry_payload, package_names = VulnersService._validate_and_process_file(requirements_file)
        start_time = datetime.datetime.now()

        url = f"{self.base_url}{CONST.QUERY_BATCH_PATH}"

        response = requests.post(url, json=qry_payload)

        if response.status_code == HTTPStatus.OK:
            data = response.json()
            vulnerability_mapping = {}
            for dependency, result in zip(package_names, data["results"]):
                vulns = result.get("vulns", [])
                if vulns:
                    vulnerability_mapping[dependency] = f"{len(vulns)} vulnerabilities found"
                else:
                    vulnerability_mapping[dependency] = "vulnerabilities NOT found!"

                data = {
                    "description": project_description,
                    "dependencies": vulnerability_mapping,
                }

            # Save the final output to the in-memory 'projects' dictionary
            self.projects[project_name] = data

            result = self.handle_response(CONST.SUCCESS_STATUS,
                                        f"Project '{project_name}' created successfully.",
                                        data={project_name: data})

        else:
            result =  VulnersService.handle_response(CONST.ERROR_STATUS,
                                                     f"Failed to fetch data for {project_name}")

        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Vulners API response received in {duration} seconds.")

        logger.info("END: Fetching vulnerability details from Vulners API.")
        return result

    @staticmethod
    def _validate_and_process_file(req_file) -> tuple:
        """
        Validate and process the uploaded file to generate a payload.

        Args:
            req_file (UploadFile): The uploaded file containing dependency data.

        Returns:
            dict: A payload in the required format.

        Raises:
            HTTPException: If the file is empty or contains invalid data.
        """
        # Read the file content
        content = req_file.file.read().decode("utf-8").strip()
        if not content:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Uploaded file is empty.")

        packages_payload = []
        packages_names = []

        keys = Config.EXPECTED_KEYS
        for line in content.splitlines():
            try:
                # Parse each line as JSON
                row = json.loads(line)
                # Look for required fields in the row
                if not all(key in row for key in keys):
                    # raise ValueError("Missing required fields in row data.")
                    packages_names.append(f"Invalid entry: {line}")

                packages_names.append(row[keys[0]]) # Assuming 'name' is the first key in EXPECTED_KEYS
                # Build the payload for each package and append to the list
                packages_payload.append({
                    "version": row[keys[1]],        # Assuming 'version' is the second key in EXPECTED_KEYS
                    "package": {
                        "name": row[keys[0]],       # Assuming 'name' is the first key in EXPECTED_KEYS
                        "ecosystem": row[keys[2]]   # Assuming 'ecosystem' is the third key in EXPECTED_KEYS,
                    }
                })
            except json.JSONDecodeError:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                    detail=f"Invalid JSON format: {line}")
            except ValueError as e:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))

        logger.debug(f"Processed {len(packages_payload)} packages from the uploaded file.")
        logger.debug(f"Packages: {packages_names}")

        # Construct the payload
        payload = {"queries": packages_payload}
        return payload, packages_names

    def handle_response(self, status: str, message: str, data: dict = {}) -> dict:
        """Standardize the API response format.

        Args:
            status (str): The status of the operation ("success" or "error").
            message (str): A descriptive message about the operation.
            data (dict): The actual data to be returned (if any). Default is an empty dict.

        Returns:
            dict: Standardized Response.
        """
        response = {
            "status": status,
            "message": message,
            "data": data
        }
        logger.debug(f"Final Response: {response}")
        return response
