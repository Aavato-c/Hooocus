import concurrent.futures
from copy import deepcopy
import datetime
import io
import random
import subprocess
import concurrent
from uuid import uuid4
import cv2
from numpy import ndarray
from sympy import EX
from h3_utils.flags import Performance
from h3_utils.launch.launch import prepare_environment
prepare_environment()

from modules.async_worker import ImageTaskProcessor
import ldm_patched.modules.model_management
from h3_utils.config import LAUNCH_ARGS, ImageGenerationObject, OverWriteControls, DefaultConfigImageGen, HooocusConfig
from unavoided_globals.global_model_management import global_model_management
from PIL import Image
from h3_utils.logging_util import LoggingUtil
log = LoggingUtil().get_logger()
import time



class BatchTemplates:
    _shared = HooocusConfig
    _shared.image_number = 1

    normal = ImageGenerationObject(
        )


imgProcessor = ImageTaskProcessor()

def generate_image_to_stream(prompt: str):
    # https://stackoverflow.com/questions/65971081/streaming-video-from-camera-in-fastapi-results-in-frozen-image-after-first-frame
    unique_id = uuid4().hex
    newtask = deepcopy(BatchTemplates.normal)
    newtask.seed = random.randint(LAUNCH_ARGS.min_seed, LAUNCH_ARGS.max_seed)
    newtask.uid = unique_id
    newtask.prompt = prompt
    newtask.performance_selection = Performance.LIGHTNING
    imgProcessor.generation_tasks.append(newtask)

    # Create and run task asynchronously
    concurrent.futures.ThreadPoolExecutor().submit(imgProcessor.process_all_tasks)
    
    finished = False
    max_loops = 1000
    while not finished:
        max_loops -= 1
        if max_loops <= 0:
            raise Exception('Max loops reached.')
        time.sleep(1.0)
        if len(imgProcessor.yields) > 0:
            try:
                img_res = imgProcessor.yields.pop(0)
            except Exception as e:
                log.error(str(e))
                time.sleep(0.05)
            if img_res[0] == "preview" and img_res[-1] == unique_id:
                (flag, encodedImage) = cv2.imencode(".jpg", img_res[2])
                if not flag:
                    continue
                else:
                    log.debug('Image preview generated.')
                    yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                            bytearray(encodedImage) + b'\r\n')
            elif img_res[0] == "result" and img_res[-1] == unique_id:
                (flag, encodedImage) = cv2.imencode(".jpg", img_res[2])
                if not flag:
                    raise Exception('Error encoding image.')
                else:
                    log.debug('Image result generated.')
                    finished = True
                    yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                            bytearray(encodedImage) + b'\r\n')
            else:
                log.debug('No image preview generated.')
                continue

def get_filename_from_image() -> str:
    dt_string = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"outputs/{dt_string}.jpg"
                

def generate_image(prompt: str, savesteps: bool = False, image_filename = None) -> bool:
    # https://stackoverflow.com/questions/65971081/streaming-video-from-camera-in-fastapi-results-in-frozen-image-after-first-frame
    unique_id = uuid4().hex
    newtask = deepcopy(BatchTemplates.normal)
    newtask.seed = random.randint(LAUNCH_ARGS.min_seed, LAUNCH_ARGS.max_seed)
    newtask.uid = unique_id
    newtask.prompt = prompt
    newtask.performance_selection = Performance.LIGHTNING
    imgProcessor.generation_tasks.append(newtask)

    # Create and run task asynchronously
    concurrent.futures.ThreadPoolExecutor().submit(imgProcessor.process_all_tasks)
    



if __name__ == '__main__':
    # overwrites = OverWriteControls(overwrite_step=15)
    prompt = 'a cat in the forest, at night oil painting'
    
    generate_image(prompt, savesteps=True)
