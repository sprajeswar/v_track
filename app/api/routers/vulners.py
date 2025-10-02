"""Endpoints for Vulnerabilities."""

from fastapi import APIRouter, UploadFile, HTTPException
from http import HTTPStatus

from app.services.vulners_service import VulnersService
from app.logger import setup_logger
from app.constants import Constants as CONST
from app.config import Config

import datetime as datetime

logger = setup_logger(__name__)

router = APIRouter()

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
    return {"status": "OK. Vulners endpoint is up and running."}

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
                response = vulners_service.handle_response(CONST.SUCCESS_STATUS,
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

    except Exception as ex:
        msg  = f"Error creating project '{name}'"
        logger.error(f"{msg}: {str(ex)}")
        response = vulners_service.handle_response(CONST.ERROR_STATUS,
                                                f"{msg}. Check logs for details.")

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

    # Check if there are no projects
    if not vulners_service.projects:
        logger.info("No projects found.")
        response = vulners_service.handle_response(CONST.SUCCESS_STATUS,
                                        "No projects found. Create a project first.")

    else: #There are projects
        projects_cnt = len(vulners_service.projects)
        logger.info(f"Total projects found: {projects_cnt}")
        logger.debug(f"Existing projects data: {vulners_service.projects}")
        filtered_projects = {}

        for project_id, project_data in vulners_service.projects.items():
            # Check if any dependency has vulnerabilities
            dependencies = project_data.get("dependencies", {})
            has_vulnerabilities = any(
                "vulnerabilities found" in status.lower() for status in dependencies.values()
            )

            if has_vulnerabilities:
                filtered_projects[project_id] = project_data

        if filtered_projects:
            msg = f"Project count: {projects_cnt}. {len(filtered_projects)} project(s) with vulnerabilities found."

            response = vulners_service.handle_response(CONST.SUCCESS_STATUS,
                                                        msg, data=filtered_projects)

        else:
            # There are projects but none have vulnerabilities
            msg = f"Project count: {projects_cnt}. No projects with vulnerabilities found."
            logger.info(f"{msg}")

            response = vulners_service.handle_response(CONST.SUCCESS_STATUS, msg)

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

    # Check if the project exists
    if not vulners_service.projects:
        logger.info("No projects found.")
        return vulners_service.handle_response(CONST.SUCCESS_STATUS,
                                        "No projects found. Create a project first.")

    project_data = vulners_service.projects.get(project_name)
    if not project_data:
        logger.info(f"Project '{project_name}' not found.")
        response = vulners_service.handle_response(CONST.SUCCESS_STATUS,
                                                f"Project '{project_name}' not found.")

    else:
        # Check if the project has any vulnerabilities
        dependencies = project_data.get("dependencies", {})
        vulnerabilities = {
                dependency: status
                    for dependency, status in dependencies.items()
                        if "vulnerabilities found" in status.lower()
                }

        if not vulnerabilities:
            logger.info(f"No vulnerabilities found for project: {project_name}")
            response = vulners_service.handle_response(CONST.SUCCESS_STATUS,
                                f"No vulnerabilities found for the project '{project_name}'.")

        else:
            response = vulners_service.handle_response(CONST.SUCCESS_STATUS,
                                f"Vulnerabilities found for the project '{project_name}'.",
                                data={"vulnerabilities": vulnerabilities})

    logger.info(f"END: Fetching vulnerabilities for project: {project_name}")
    return response
