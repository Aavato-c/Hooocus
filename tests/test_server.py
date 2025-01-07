from calendar import c
import subprocess
import os, sys
from turtle import st

from numpy import mat
from sympy import content

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURR_DIR.split("tests")[0])
import consts
import time
import os, sys, dotenv, pytest
import threading
from requests import Session as RequestsSession

from h3_utils.config import ImageGenerationObject
from h3_utils.logging_util import LoggingUtil

from tests.utils_for_testing import test_client_main

dotenv.load_dotenv()

ACCEPTED_API_TOKEN_FOR_IMAGE_GENERATION = os.environ.get("ACCEPTED_API_TOKEN_FOR_IMAGE_GENERATION")

log = LoggingUtil(__name__).get_logger()

# GLOBAL VAR USAGE
# Affects the database connection in db/database.py (get_db_unmanaged)
consts.TESTING = True

class DataManager:
    client = test_client_main

    def __init__(self):
        self.session = RequestsSession()
        self.test_token = ACCEPTED_API_TOKEN_FOR_IMAGE_GENERATION
        self.headers_for_auth = {"Authorization": f"Bearer {self.test_token}"}
        self.client.headers.update(self.headers_for_auth)
        self.uuid_of_photo = None


@pytest.fixture(name="data_manager", scope="module", autouse=True)
def data_manager_fixture() -> DataManager:
    return DataManager()

def test_create_image_order(data_manager: DataManager):
    new_image_order = ImageGenerationObject()
    new_image_order.prompt = "Cat oil painting sun moon smoke classical museum portrait painting oil on canvas rembrandt"
    response = data_manager.client.post("/gen/photo/normal", data=new_image_order.model_dump_json())
    if response.status_code == 201:
        assert True
        response_json = response.json()
    else:
        log.error(f"Failed to create image order: {response.status_code}")
    
    assert "uuid" in response_json
    uuid_of_photo = response_json["uuid"]
    data_manager.uuid_of_photo = uuid_of_photo

def test_getphoto(data_manager: DataManager):
    uuid_of_photo = data_manager.uuid_of_photo

    with data_manager.client.stream("GET", f"/photo/{uuid_of_photo}.webp") as response:
        iternum = 0
        for chunk in response.iter_bytes():
            read_resp = chunk
            content = read_resp.decode("utf-8")
            with open(f"tests/iters/content.txt", "w") as f:
                f.write(content)




def test_teardown(data_manager: DataManager):
    data_manager.session.close()


if __name__ == "__main__":
    pytest.main([__file__, "-W", "ignore::pytest.PytestAssertRewriteWarning"])
