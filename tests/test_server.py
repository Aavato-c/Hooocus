import os
from random import randbytes


import urllib
# These variables are used in the auth/auth_handlers.py:verify_user function

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # To solve the problem of importing modules from different directories
os.sys.path.insert(0,parentdir) 



import httpx
import pytest
from requests import Session
import dotenv

from fastapi import Response

from utils_for_testing import test_client_main
from h3_utils.logging_util import LoggingUtil

dotenv.load_dotenv()
log = LoggingUtil(name="TESTING").get_logger()



#client = test_client_main


session = Session()

def test_getphoto():
    response = session.get("http://127.0.0.1:8000/getphoto/this_is_a_test_cat_oil_painting_sun_moon", stream=True)
    if response.status_code == 200:
        for chunk in response.iter_content(chunk_size=8192):
            log.info(f"Got stream bit of size {len(chunk)}")
            log.info(f"Chunk: ...{chunk[-10:]}")
    else:
        log.error(f"Failed to get photo: {response.status_code}")

if __name__ == "__main__":
    test_getphoto()
