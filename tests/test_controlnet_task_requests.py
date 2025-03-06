import os, sys

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURR_DIR.split("tests")[0])

import consts
import dotenv
import pytest
from requests import Session as RequestsSession
from modules.model_file_utils.model_file_config import ControlNetTasks

from h3_utils.config import ImageGenerationObject
from h3_utils.logging_util import LoggingUtil

dotenv.load_dotenv()

ACCEPTED_API_TOKEN_FOR_IMAGE_GENERATION = os.environ.get("ACCEPTED_API_TOKEN_FOR_IMAGE_GENERATION")
url_base = consts.SERVER_URL_LOCAL
from tests.test_params import faceswap_reference_image_url, faceswap_target_image_url
log = LoggingUtil(__name__).get_logger()

class DataManager:
    session = RequestsSession()

    def __init__(self):
        self.session = RequestsSession()
        self.uuid_of_photo = None
        self.test_token = ACCEPTED_API_TOKEN_FOR_IMAGE_GENERATION
        self.headers_for_auth = {"Authorization": f"Bearer {self.test_token}"}

@pytest.fixture(name="data_manager", scope="module", autouse=True)
def data_manager_fixture() -> DataManager:
    return DataManager()

def test_create_image_order_cdps(data_manager: DataManager):
    new_image_order = ImageGenerationObject()
    new_image_order.prompt = "Cat oil painting sun moon smoke classical museum portrait painting oil on canvas rembrandt"
    
    faceswap_reference = ControlNetTasks.FaceSwap
    faceswap_reference.image_url = faceswap_reference_image_url

    faceswap_target = ControlNetTasks.PyraCanny
    faceswap_target.image_url = faceswap_target_image_url

    new_image_order.controlnet_tasks.append(faceswap_reference)
    new_image_order.controlnet_tasks.append(faceswap_target)
    response = data_manager.session.post(f"{url_base}/photo", data=new_image_order.model_dump_json(), headers=data_manager.headers_for_auth)
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

    response = data_manager.session.get(f"{url_base}/photo/{uuid_of_photo}.webp", stream=True)
    iternum = 1
    for chunk in response.iter_content():
        iternum += 1
        read_resp = chunk
        _content = read_resp  # Skip decoding for image data
        pass

    assert iternum > 1

        





def test_teardown(data_manager: DataManager):
    data_manager.session.close()


if __name__ == "__main__":
    pytest.main([__file__])
