"""API - Top level module for the application."""

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware

from app.rate_limiter import limiter
from app.api.routers import vulners
from app.logger import setup_logger
from app.constants import Constants as CONST
from app.utils.response_utils import handle_response
from app.token_auth import get_api_key

import datetime as datetime

app = FastAPI()
app.state.limiter = limiter
app.add_middleware (SlowAPIMiddleware)

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Ingect routers
app.include_router(vulners.router, tags=["Vulnerability APIs"])

logger = setup_logger(__name__)

@app.get("/")
def health():
    """Health check endpoint."""
    logger.info("Top level Health check endpoint called.")
    return handle_response(
        status=CONST.SUCCESS_STATUS,
        message="Service is up and running.",
        data={}
    )



