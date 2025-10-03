"""Service to interact with Vulners API."""

from fastapi import HTTPException, UploadFile
from http import HTTPStatus

from app.constants import Constants as CONST
from app.logger import setup_logger
from app.config import Config
from app.utils.response_utils import handle_response

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

        qry_payload, package_names = self._validate_and_process_file(requirements_file)
        start_time = datetime.datetime.now()

        url = f"{self.base_url}{CONST.QUERY_BATCH_PATH}"

        response = requests.post(url, json=qry_payload)

        if response.status_code == HTTPStatus.OK:
            data = response.json()
            logger.debug(f"Vulners API response: {data}")
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

            result = handle_response(CONST.SUCCESS_STATUS,
                                        f"Project '{project_name}' created successfully.",
                                        data={project_name: data})

        else:
            result =  handle_response(CONST.ERROR_STATUS,
                                        f"Failed to fetch data for {project_name}")

        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Vulners API response received in {duration} seconds.")

        logger.info(f"RESULT: {result}")
        logger.info("END: Fetching vulnerability details from Vulners API.")
        return result

    @staticmethod
    def _read_file(req_file: UploadFile) -> str:
        """
        Read the content of the uploaded file.

        Args:
            req_file (UploadFile): The uploaded file.

        Returns:
            str: The content of the file as a string.

        Raises:
            HTTPException: If the file is empty.
        """
        content = req_file.file.read().decode("utf-8").strip()

        if not content:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Uploaded file is empty.")

        return content

    @staticmethod
    def _validate_file_content(content: str, expected_keys: list) -> list:
        """
        Validate the content of the file.

        Args:
            content (str): The content of the file as a string.
            expected_keys (list): The list of expected keys in each row.

        Returns:
            list: A list of valid rows from the file.

        Raises:
            HTTPException: If the content contains invalid JSON or missing fields.
        """
        valid_rows = []
        for line in content.splitlines():
            try:
                row = json.loads(line)
                if not all(key in row for key in expected_keys):
                    raise ValueError(f"Missing required fields in row: {line}")
                valid_rows.append(row)

            except json.JSONDecodeError:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Invalid JSON format: {line}")

            except ValueError as vex:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Invalid value found: {str(vex)}")

        return valid_rows

    @staticmethod
    def _build_payload(valid_rows: list, expected_keys: list) -> tuple:
        """
        Build the payload and extract package names from the validated rows.

        Args:
            valid_rows (list): A list of validated rows.
            expected_keys (list): The list of expected keys in each row.

        Returns:
            tuple: A tuple containing the payload and the list of package names.
        """
        packages_payload = []
        package_names = []

        for row in valid_rows:
            package_names.append(row[expected_keys[0]])  # Assuming 'name' is the first key
            packages_payload.append({
                "version": row[expected_keys[1]],        # Assuming 'version' is the second key
                "package": {
                    "name": row[expected_keys[0]],       # Assuming 'name' is the first key
                    "ecosystem": row[expected_keys[2]]   # Assuming 'ecosystem' is the third key
                }
            })

        payload = {"queries": packages_payload}
        return payload, package_names

    def _validate_and_process_file(self, req_file: UploadFile) -> tuple:
        """
        Validate and process the uploaded file to generate a payload.

        Args:
            req_file (UploadFile): The uploaded file containing dependency data.

        Returns:
            tuple: A tuple containing the payload and the list of package names.
        """
        content = VulnersService._read_file(req_file)
        valid_rows = VulnersService._validate_file_content(content, Config.EXPECTED_KEYS)
        payload, package_names = VulnersService._build_payload(valid_rows, Config.EXPECTED_KEYS)

        logger.debug(f"Processed {len(payload['queries'])} packages from the uploaded file.")
        logger.debug(f"Packages: {package_names}")
        return payload, package_names

