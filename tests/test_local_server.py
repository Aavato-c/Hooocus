import json
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

custom_req = "{\"uid\":\"<<UUID>>\",\"do_not_update_seed\":false,\"negative_prompt\":\"\",\"use_prompt_expansion\":true,\"prompt\":\"Kael has a ruggedly handsome face with chiseled features, a lean but muscular body, and typically sports a fitted leather jacket over a simple black shirt and worn jeans, giving him a rebellious yet approachable look.\",\"aspect_ratio\":\"832*1152\",\"seed\":5401321607607695004,\"additional_style_lamdas\":[],\"sample_sharpness\":10.5,\"styles\":[],\"performance_selection\":\"Speed\",\"sampler_name\":\"dpmpp_2m_sde_gpu\",\"scheduler_name\":\"karras\",\"adaptive_cfg\":7.0,\"cfg_scale\":3.0,\"cfg_tsnr\":7.0,\"adm_scaler_end\":0.2,\"adm_scaler_negative\":0.8,\"adm_scaler_positive\":1.5,\"canny_high_threshold\":128,\"canny_low_threshold\":64,\"controlnet_softness\":0.25,\"controlnet_tasks\":[],\"input_image\":null,\"input_image_url\":null,\"uov_input_image\":null,\"input_mask_image\":null,\"prepared_input_mask_image\":null,\"enhance_input_image\":null,\"image_input_mode\":\"uov\"}"
custom_req_new_uuid = custom_req.replace("<<UUID>>", str(get_uuid()))


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

def test_custom_request(data_manager: DataManager):
    response = data_manager.client.post("/gen/photo/normal", data=custom_req_new_uuid)
    response_json = response.json()
    if response.status_code == 201:
        assert True
    else:
        log.error(f"Failed to create image order: {response.status_code}")

    assert "uuid" in response_json
    uuid_of_photo = response_json["uuid"]
    data_manager.uuid_of_photo = uuid_of_photo

    url_for_photo = f"/photo/{uuid_of_photo}.webp"
    with data_manager.client.stream("GET", f"/photo/{uuid_of_photo}.webp") as response:
        iternum = 0
        for chunk in response.iter_bytes():
            read_resp = chunk
            iternum += 1

    assert iternum > 0

def test_teardown(data_manager: DataManager):
    data_manager.session.close()


if __name__ == "__main__":
    pytest.main([__file__, "-W", "ignore::pytest.PytestAssertRewriteWarning"])
