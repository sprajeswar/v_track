"""Place for 'rate limiter' for End Points"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import Config

limiter = Limiter(key_func=get_remote_address,
                default_limits=[f"{Config.NUM_TIMES}/{Config.TYPE_LIMIT}"])

#limiter.limit("#/text")
    ##text as minute/second/hour
#limiter.exempt