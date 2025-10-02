"""API - Top level module for the application."""

from fastapi import FastAPI

from app.api.routers import vulners
from app.logger import setup_logger

import datetime as datetime

logger = setup_logger(__name__)

app = FastAPI()
app.include_router(vulners.router)

@app.get("/")
def health():
    """Health check endpoint."""
    logger.info("Top level Health check endpoint called.")
    return {"status": "OK. Server is up and running."}



