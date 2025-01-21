import os, sys
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURR_DIR.split("tests")[0])
import random
import consts
from h3_utils.flags import SDXL_ASPECT_RATIOS_CLASS, Performance
from tests.test_gen_to_server import ImageType, get_image_link
import time
import os, sys, dotenv, pytest
import threading
from requests import Session as RequestsSession

from h3_utils.config import ImageGenerationObjectForRequests
from h3_utils.logging_util import LoggingUtil

from tests.utils_for_testing import get_uuid, test_client_main

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
    new_image_order = ImageGenerationObjectForRequests()
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
            iternum += 1

    assert iternum > 0


def test_genphoto(data_manager: DataManager):
    uid = get_uuid()
    test_request = ImageGenerationObjectForRequests(
        sample_sharpness=10.5,
        performance_selection=Performance.SPEED,
        seed=random.randint(0, 100000),
        prompt="A beautiful sunset over the ocean with two cats playing in the sand",
        aspect_ratio=SDXL_ASPECT_RATIOS_CLASS.LANDSCAPE.R_1280_768,
    )
    response = data_manager.client.post("/gen/photo/normal", data=test_request.model_dump_json())
    if response.status_code == 201:
        assert True
        response_json = response.json()
    else:
        log.error(f"Failed to create image order: {response.status_code}")

    assert "uuid" in response_json
    uuid_of_photo = response_json["uuid"]
    data_manager.uuid_of_photo = uuid_of_photo

    with data_manager.client.stream("GET", f"/gen/photo/{uuid_of_photo}.webp") as response:
        iternum = 0
        for chunk in response.iter_bytes():
            read_resp = chunk
            iternum += 1

    assert iternum > 0


def test_teardown(data_manager: DataManager):
    data_manager.session.close()


if __name__ == "__main__":
    pytest.main([__file__, "-W", "ignore::pytest.PytestAssertRewriteWarning"])
