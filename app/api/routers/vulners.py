"""Endpoints for Vulnerabilities."""

from fastapi import APIRouter, UploadFile, HTTPException
from fastapi import Request, Depends

from app.rate_limiter import limiter
from app.services.vulners_service import VulnersService
from app.logger import setup_logger
from app.constants import Constants as CONST
from app.config import Config
from app.utils.response_utils import handle_response
from app.token_auth import get_api_key

import datetime as datetime

logger = setup_logger(__name__)

router = APIRouter(dependencies = [Depends(get_api_key)])

# Create a shared instance of VulnersService
# This is to ensure that the in-memory 'projects' dictionary
# is shared across all requests.
vulners_service = VulnersService()

@router.get("/health")
def check_health():
    """
    Health check endpoint for the Vulners router.
    This verifies if the Vulners router is working.
    """
    return handle_response(
        status=CONST.SUCCESS_STATUS,
        message="Router Vulnerability end points are good.",
        data={}
    )

@router.post("/project")
def create_vulnerability_project(name: str, description: str, requirements: UploadFile):
    """
    Create a new vulnerability project.
    requirements file: each line format like below
        {"name": "Django", "version": "3.0.0", "ecosystem": "PyPI"}

    Args:
        name (str): Name of the project.
        description (str): Description of the project.
        requirements (UploadFile): Requirements file containing package details.

    Returns:
        dict: Response from the Vulners service.
    """
    logger.info(f"START: Creating vulnerability project: {name}")

    start_time = datetime.datetime.now()
    try:
        if name in vulners_service.projects.keys():
            if not Config.REDO_FOR_SAME_PROJECT:
                response = handle_response(CONST.SUCCESS_STATUS,
                                                    f"Project with name '{name}' already exists.")

            else:
                logger.warning(f"Flag in Config is set to {Config.REDO_FOR_SAME_PROJECT}.")
                logger.warning(f"Project '{name}' already exists  and overwiriting.")
                response = vulners_service.create_project(project_name = name,
                                                project_description = description,
                                                requirements_file = requirements)

        else:
            response = vulners_service.create_project(project_name = name,
                                                project_description = description,
                                                requirements_file = requirements)

    except HTTPException as http_ex:
        logger.info(f"HTTPException occurred: {http_ex.detail}")
        response = handle_response(CONST.ERROR_STATUS, http_ex.detail)

    except Exception as ex:
        # Handle generic exceptions
        logger.error(f"Unexpected error occurred: {str(ex)}")
        response = handle_response(CONST.ERROR_STATUS,
                                                f"An unexpected error occurred: {str(ex)}")
    finally:
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Project '{name}' created in {duration} seconds.")

    logger.debug(response)
    logger.info(f"END: Creating vulnerability project: {name}")

    return response

@router.get("/projects")
def get_projects() -> dict:
    """
    Method to retrieve all projects with vulnerabilities.
    Scenarios:
    1. No Projects created
    2. Projects available but none with vulnerabilities
    3. Projects available with some having vulnerabilities

    Returns:
        dict: Response dict.
    """
    logger.info("START: Retrieving all vulnerability projects.")
    response = vulners_service.get_projects()
    logger.info("END: Retrieving all vulnerability projects.")
    return response

@router.get("/projects/{project_name}")
def get_project_vulnerabilities(project_name: str) -> dict:
    """
    End point to fetch vulnerabilities for a specific project.
    Scenarios:
        1. Projects are not created
        2. Given Project not found
        3. Given Project found but no vulnerabilities
        4. Given Project found with vulnerabilities

    Args:
        project_name (str): The name of the project.

    Returns:
        dict: Vulnerabilities for the project or a message if none are found.
    """
    logger.info(f"START: Fetching vulnerabilities for project: {project_name}")

    if not project_name  or not project_name.strip():
        logger.error("Package name is missing and required.")
        return handle_response(CONST.ERROR_STATUS,
                                        "Package name is required.")
    # Check if the project exists
    if not vulners_service.projects:
        logger.info("No projects found.")
        return handle_response(CONST.SUCCESS_STATUS,
                                        "No projects found. Create a project first.")

    project_data = vulners_service.projects.get(project_name)

    if not project_data:
        logger.info(f"Project '{project_name}' not found.")
        response = handle_response(CONST.SUCCESS_STATUS,
                                                f"Project '{project_name}' not found.")

    else:
        dependencies = project_data.get("dependencies", {})
        response = handle_response(CONST.SUCCESS_STATUS,
                                f"Vulnerabilities found for the project '{project_name}'.",
                                data={project_name: dependencies})
    return response

@router.get("/all_dependencies")
def get_all_dependencies() -> dict:
    """
    Endpoint to fetch all dependencies across all projects created.
    Scenarios:
        1. No Projects created
        2. Projects available but none with dependencies
        3. Projects available with some having dependencies

    Returns:
        dict: Response dict.
    """
    logger.info("START: Retrieving all dependencies across projects.")

    # Check if there are no projects
    if not vulners_service.projects:
        logger.info("No projects found.")
        response = handle_response(CONST.SUCCESS_STATUS,
                                        "No projects found. Create a project first.")

    else:
        response = vulners_service.pull_dependencies()

    logger.info("END: Retrieving all dependencies across projects.")
    return response

@router.get("/dependency")
def get_package_dependencies(package_name: str, package_version: str, ecosystem: str = "PyPI") -> dict:
    """
    Endpoint to fetch dependency for a given package.
    Payload format:{
            "version": "2.3.3",
            "package": {
                "name": "pandas",
                "ecosystem": "PyPI"
            }
         }

    Returns:
        dict: Response dict.
    """
    logger.info("START: Retrieving all dependencies with vulnerabilities across projects.")

    if package_name is None or package_version is None:
        logger.error("Package name and version are required.")
        response = handle_response(CONST.ERROR_STATUS,
                                        "Package name and version are required.")
    else:
        payload = {
            "version": package_version,
            "package": {
                "name": package_name,
                "ecosystem": ecosystem
            }
        }
        logger.debug(f"Payload for single dependency: {payload}")
        response = vulners_service.get_package_vulnerabilities(payload)

    logger.info("END: Retrieving all dependencies with vulnerabilities across projects.")
    return response