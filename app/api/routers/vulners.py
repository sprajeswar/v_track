"""Endpoints for Vulnerabilities."""

from fastapi import APIRouter
from app.services import vulners_service
from app.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

@router.get("/vulners/health")
def check_vulners_health():
    """
    Health check endpoint for the Vulners router.
    This verifies if the Vulners router is working.
    """
    return {"status": "OK. Vulners endpoint is up and running."}

@router.post("/project")
def create_vulnerability_project(name: str, description: str):
    """
    Create a new vulnerability project.

    Args:
        name (str): Name of the project.
        description (str): Description of the project.

    Returns:
        dict: Response from the Vulners service.
    """
    vulners_service_instance = vulners_service.VulnersService()
    response = vulners_service_instance.get_vulnerability()

    logger.info(response)
    return response