"""API - Top level module for the application."""

from fastapi import FastAPI

from app.api.routers import vulners
from app.logger import setup_logger
from app.constants import Constants as CONST
from app.utils.response_utils import handle_response

import datetime as datetime

logger = setup_logger(__name__)

app = FastAPI()
app.include_router(vulners.router)

@app.get("/")
def health():
    """Health check endpoint."""
    logger.info("Top level Health check endpoint called.")
    return handle_response(
        status=CONST.SUCCESS_STATUS,
        message="Service is up and running.",
        data={}
    )



