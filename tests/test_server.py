import os, sys, dotenv, pytest
from requests import Session as RequestsSession
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURR_DIR.split("tests")[0])

from h3_utils.config import ImageGenerationObject
from h3_utils.logging_util import LoggingUtil

from tests.utils_for_testing import test_client_main

import db.models as dbm

dotenv.load_dotenv()

ACCEPTED_API_TOKEN_FOR_IMAGE_GENERATION = os.environ.get("ACCEPTED_API_TOKEN_FOR_IMAGE_GENERATION")

log = LoggingUtil(name="TESTING").get_logger()

class DataManager:
    client = test_client_main

    def __init__(self):
        self.test_token = ACCEPTED_API_TOKEN_FOR_IMAGE_GENERATION
        self.headers_for_auth = {"Authorization": f"Bearer {self.test_token}"}
        self.client.headers.update(self.headers_for_auth)

@pytest.fixture(name="data_manager", scope="module")
def data_manager_fixture() -> DataManager:
    return DataManager()


def test_setups_for_tests(self, data_manager: DataManager):
    new_image_order = ImageGenerationObject()
    new_image_order.prompt = "Cat oil painting sun moon smoke classical museum portrait painting oil on canvas rembrandt"
    response = data_manager.client.post("/getphoto", data=new_image_order.model_dump_json())
    assert response.status_code == 200
    


def test_getphoto():
    #response = session.get("http://127.0.0.1:8000/getphoto/this_is_a_test_cat_oil_painting_sun_moon", stream=True)
    response = test_client_main.get("/this_is_a_test_cat_oil_painting_sun_moon.jpg", allow_redirects=True)
    if response.status_code == 200:
        """ for chunk in response.iter_content(chunk_size=8192):
            log.info(f"Got stream bit of size {len(chunk)}")
            log.info(f"Chunk: ...{chunk[-10:]}") """
        pass
    else:
        log.error(f"Failed to get photo: {response.status_code}")

if __name__ == "__main__":
    pytest.main([__file__, "-W", "ignore::pytest.PytestAssertRewriteWarning"])
