"""Simple Token based authorization"""

from fastapi import Security, Depends, HTTPException
from fastapi.security import APIKeyHeader
from http import HTTPStatus
from app.config import Config


SECRET_KEY_TOKEN = Config.SECRET_KEY_TOKEN

api_key_header = APIKeyHeader(name = "X-API-Token", auto_error = True)

def get_api_key (api_key: str = Security(api_key_header)):
    if api_key!= SECRET_KEY_TOKEN:
        raise HTTPException(status_code = HTTPStatus.UNAUTHORIZED,
                            detail = "Missing or invalid token!!!")
    return api_key
