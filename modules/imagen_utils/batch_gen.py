# nohup sh rungen.sh > rungen2.log 2>&1 &
import random
import json, os, sys
from uuid import uuid4

from torch import rand

currdir = os.path.abspath(__file__)
sys.path.append(currdir.split("Hooocus")[0] + "Hooocus")

from h3_utils.logging_util import LoggingUtil
from h3_utils.config import ImageGenerationObject, ImageGenerationObjectForRequests
from h3_utils.flags import SDXL_ASPECT_RATIOS_CLASS, Performance
from modules.imagen_utils.imagen_main import generate_from_batch

log = LoggingUtil("batch_gen").get_logger()

def add_imageorders_from_json(json_path: str, outputlog: str, n: int = 3):
    """
    Reads a JSON file and adds image orders to the database.
    """
    lognum = random.randint(0, 2**63 - 1)
    with open(json_path, "r") as f:
        data = json.load(f)

    outputlog = outputlog.replace(".json", f"_{lognum}.json")
    log.info(f"Output log file: {outputlog}")
    for item in data:
        for i in range(n):
            imagen_request_base = ImageGenerationObjectForRequests(
                sample_sharpness=10.5,
                cfg_scale=2.0,
                performance_selection=Performance.SPEED,
                
                
                )
            imagen_request_base.seed = random.randint(0, 2**63 - 1)
            imagen_request_base.uid = str(uuid4())
            imagen_request_base.prompt = item["image_prompt"]
            imagen_request_base.aspect_ratio = SDXL_ASPECT_RATIOS_CLASS.LANDSCAPE.R_1280_768
            log.info(f"Generating image {i} for id {imagen_request_base.uid} (Item: {item['id']})")
            
            try:
                if item["image_paths"]:
                    item["image_paths"] = item["image_paths"].append(f"{imagen_request_base.uid}.webp")
                else:
                    item["image_paths"] = [f"outputs/{imagen_request_base.uid}.webp"]
            except KeyError:
                item["image_paths"] = [f"outputs/{imagen_request_base.uid}.webp"]

            try:
                generate_from_batch(imagen_request_base, imagen_request_base.uid)
            except Exception as e:
                print(f"Error generating image: {e}")
                return
            
            if os.path.exists(outputlog):
                with open(outputlog, "r") as log_file:
                    log_data = json.load(log_file)
                    log_data.append(item)
            else:
                log_data = [item]
            with open(outputlog, "w") as log_file:
                json.dump(log_data, log_file, indent=4, ensure_ascii=False)
            

        

        
if __name__ == "__main__":
    json_path = "tests/batch.json"
    outputlog = "tests/batch_log.json"
    add_imageorders_from_json(json_path, outputlog)
        