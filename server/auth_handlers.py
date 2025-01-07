import sys, os
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURR_DIR.split("server")[0])

from consts import ACCEPTED_API_TOKEN_FOR_IMAGE_GENERATION
from h3_utils.logging_util import LoggingUtil

from fastapi.security import OAuth2
from fastapi import Depends, HTTPException

from typing import Annotated



logger = LoggingUtil(__name__)
log = logger.get_logger()

oauth2_scheme = OAuth2()

async def verify_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
            token = token.replace("Bearer ", "")
            if token != ACCEPTED_API_TOKEN_FOR_IMAGE_GENERATION:
                raise HTTPException(status_code=401, detail="")
            return True
    except Exception as e:
        log.error(f"Error verifying user: {e}")
        raise HTTPException(status_code=401, detail="")

