"""Service to interact with Vulners API."""

from fastapi import HTTPException, UploadFile
from http import HTTPStatus
from functools import lru_cache

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
            "queries": [
                {"package": {"name": "Django", "ecosystem": "PyPI"}, "version": "3.2.0"}
            ]
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

        url = f"{CONST.SERVER}{CONST.API_VERSION}{CONST.QUERY_BATCH_PATH}"
        response = self.call_api(url, json.dumps(qry_payload))

        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Vulners API response received in {duration} seconds.")

        result = self._process_api_response(response, project_name, project_description, package_names)

        logger.info(f"RESULT: {result}")
        logger.info("END: Fetching vulnerability details from Vulners API.")
        return result

    def _process_api_response(self, response: requests.Response, project_name: str,
                               project_description: str, package_names: list) -> dict:
        """Process the API response and store the results in the in-memory 'projects' dictionary.
        Args:
            response (requests.Response): The response from the Vulners API.
            project_name (str): Name of the project.
            project_description (str): Description of the project.
            package_names (list): List of package names queried.
        Returns:
            dict: The processed result
        """ 
        logger.info("START: Processing API response.")
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

        logger.info("END: Processing API response.")
        return result

    @staticmethod
    @lru_cache(maxsize=Config.LRU_CACHE_SIZE, typed=Config.LRU_CACHE_TYPED)
    def call_api(url: str, payload: str) -> dict:
        """
        Call the Vulners API with the given payload.

        Args:
            url (str): End point for API
            payload (str): The JSON payload as a string.

        Returns:
            dict: The API response.
        """
        logger.info(VulnersService.call_api.cache_info())

        logger.debug(url)
        logger.debug(payload)
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=payload, headers=headers)

        return response

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
        logger.debug(f"Payload: {payload}")
        return payload, package_names

    def pull_dependencies(self)-> dict:
        """Pull dependencies with vulnerabilities across all projects.

        Returns:
            dict: A dictionary with dependencies as keys
                and list of projects with vulnerability counts as values.
        """
        logger.info("START: Pulling dependencies with vulnerabilities across all projects.")
        try:
            result = {}
            for project, details in self.projects.items():
                for dep, status in details["dependencies"].items():
                    vuln_cnt = "".join(filter(str.isdigit, status)) or "0"
                    if int(vuln_cnt) > 0:
                        key = dep.lower()
                        if key not in result:
                            result[key] = []
                        result[key].append(f"{project}: {vuln_cnt}")
            final_result = {key: ", ".join(val) for key, val in result.items()}

            if final_result:
                logger.info(f"Final dependencies with vulnerabilities: {final_result}")
                response = handle_response(CONST.SUCCESS_STATUS,
                            "Fetched dependencies with vulnerabilities across all projects.",
                            data={"dependencies": final_result})
            else:
                msg = "No dependencies with vulnerabilities found across projects."
                logger.info(f"{msg}")
                response = handle_response(CONST.SUCCESS_STATUS, msg)

        except Exception as ex:
            logger.error(f"Error while pulling dependencies: {str(ex)}")
            response = handle_response(CONST.ERROR_STATUS,
                            "Failed to pull dependencies with vulnerabilities.")

        logger.info("END: Pulling dependencies with vulnerabilities across all projects.")
        return response

    def get_package_vulnerabilities(self, pkg_payload: dict) -> dict:
        """Fetch vulnerability details from Vulners API for
        a given package as part of payload.

        Args:
            pkg_payload (dict): Payload for the package.

        Returns:
            dict: Final response dict.
        """
        logger.info("START: Fetching vulnerability details from Vulners API for a package.")
        start_time = datetime.datetime.now()

        url = f"{CONST.SERVER}{CONST.API_VERSION}{CONST.QUERY_PATH}"
        response = self.call_api(url, json.dumps(pkg_payload))

        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Vulners API response received in {duration} seconds.")

        project_name = pkg_payload["package"]["name"]
        version = pkg_payload["version"]
        vulns_list = response.json().get("vulns", [])
        simplified_vulns: dict = {}

        # Unsure of what to pull!!!
        for vuln in vulns_list or []:
            if not isinstance(vuln, dict):
                continue

            ## There are some with mismatched pattern!
            simplified_vulns[vuln.get("id")] = {
                "summary": vuln.get("summary") or "N/A",
                "details": vuln.get("details") or "N/A"
            }

        # This is for final response and to make sure of always return a valid dictionary
        safe_data = {
            project_name: {
                "version": version,
                "vulnerabilities": simplified_vulns
            }
        }

        status = CONST.SUCCESS_STATUS if simplified_vulns else CONST.ERROR_STATUS
        msg = (f"'{project_name}' dependencies with vulnerabilities pulled successfully."
                    if simplified_vulns else
                            f"Failed to pull dependencies with vulnerabilities for '{project_name}'.")
        logger.info("END: Fetching vulnerability details from Vulners API for a package.")
        return handle_response(status, msg, data=safe_data)

    def get_projects(self) -> dict:
        """Methos to return all the project created
            in the required format

        Returns:
            dict: Final response dict.
        """
        # Check if there are no projects
        if not self.projects:
            logger.info("No projects found.")
            response = handle_response(CONST.SUCCESS_STATUS,
                                            "No projects found. Create a project first.")

        else: #There are projects
            projects_cnt = len(self.projects)
            logger.info(f"Total projects found: {projects_cnt}")
            logger.debug(f"Existing projects data: {self.projects}")
            filtered_projects = {}

            vulnr_cntr = 0
            for project_name, project_data in self.projects.items():
                # Check if any dependency has vulnerabilities
                project = {}
                project["description"] = project_data["description"]
                dependencies = project_data.get("dependencies", {})
                has_vulnerabilities = any(
                    "vulnerabilities found" in status.lower() for status in dependencies.values()
                )

                if has_vulnerabilities:
                    project["vulnerable_dependencies"] = True
                    vulnr_cntr += 1
                else:
                    project["vulnerable_dependencies"] = False

                filtered_projects[project_name] = project

            msg = f"Project count: {projects_cnt}. {vulnr_cntr} project(s) with vulnerabilities found."

            response = handle_response(CONST.SUCCESS_STATUS, msg, data=filtered_projects)

        return response

if __name__ == "__main__":
    # Lets run locally for service validation
    vulners_service = VulnersService()

    for cnt in range(3):
        logger.info(f"Call count: {cnt+1}")
        payload = json.dumps({
            "queries": [
                {"package": {"name": "Django", "ecosystem": "PyPI"}, "version": "3.2.0"}
            ]
        })
        url = f"{CONST.SERVER}{CONST.API_VERSION}{CONST.QUERY_BATCH_PATH}"
        response = vulners_service.call_api(url, payload)
        logger.info(response)

    ## Uncomment the below for running with LRU cache validation with some other package
    # for cnt in range(3):
    #     logger.info(f"Call count: {cnt+1}")
    #     payload = json.dumps({
    #         "queries": [
    #             {"package": {"name": "requests", "ecosystem": "PyPI"}, "version": "2.25.1"}
    #         ]
    #     })