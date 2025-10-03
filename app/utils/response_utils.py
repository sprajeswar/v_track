"""Place for common utility functions."""

from app.logger import setup_logger

logger = setup_logger(__name__)


def handle_response(status: str, message: str, data: dict = {}) -> dict:
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
