import concurrent.futures
from copy import deepcopy
import datetime
import io
from operator import not_
import random
import subprocess
import concurrent
import threading
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
from PIL import Image, ImageDraw, ImageFont
from h3_utils.logging_util import LoggingUtil
import time
from unavoided_globals.unavoided_global_vars import IPM

log = LoggingUtil(name="imagen_main.py").get_logger()

DEBUG_IMAGEN = False


class BatchTemplates:
    _shared = HooocusConfig
    _shared.image_number = 1

    normal = ImageGenerationObject(
        )

if not IPM.exists_imageprocess:
    IPM.imgProcessorGlobal = ImageTaskProcessor()
    global_model_management.interrupt_processing = False
    IPM.imgProcessorGlobal.reset_cuda_memory()
    exists_imageprocess = True
    threading.Thread(target=IPM.imgProcessorGlobal.process_all_tasks, daemon=True).start()
    log.info('Image processor started.')
    imgProcessor = IPM.imgProcessorGlobal
else:
    log.info('Image processor already exists.')
    imgProcessor = IPM.imgProcessorGlobal

def _generate_image_with_text(prompt: str) -> bool:
    # For generating image bytearrays for sending visual information

    # Generate image
    img = Image.new('RGB', (640, 480), color = (0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default().font_variant(size=40)
    d.text((10,10), prompt, fill=(255,255,255), align='center', font=font)

    # Convert to byte array
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr




not_ready_arr = _generate_image_with_text('Not ready.')
waiting_arr = _generate_image_with_text('Waiting...')

def generate_image_to_stream(prompt: str):
    # https://stackoverflow.com/questions/65971081/streaming-video-from-camera-in-fastapi-results-in-frozen-image-after-first-frame
    unique_id = uuid4().hex
    newtask = deepcopy(BatchTemplates.normal)
    newtask.seed = random.randint(LAUNCH_ARGS.min_seed, LAUNCH_ARGS.max_seed)
    newtask.uid = unique_id
    newtask.prompt = prompt
    newtask.performance_selection = Performance.LIGHTNING


    imgProcessor.generation_tasks.append(newtask)
    
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
                    if not DEBUG_IMAGEN:
                        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
                    else:
                        yield f"Image preview generated: {max_loops}"
            elif img_res[0] == "result" and img_res[-1] == unique_id:
                (flag, encodedImage) = cv2.imencode(".jpg", img_res[2])
                if not flag:
                    raise Exception('Error encoding image.')
                else:
                    log.debug('Image result generated.')
                    finished = True
                    if not DEBUG_IMAGEN:
                        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
                    else:
                        yield f"Image result generated: {max_loops}"
            else:
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + not_ready_arr + b'\r\n')
                continue

def get_filename_from_image() -> str:
    dt_string = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"outputs/{dt_string}.jpg"
                

def generate_image(prompt: str) -> bool:
    # https://stackoverflow.com/questions/65971081/streaming-video-from-camera-in-fastapi-results-in-frozen-image-after-first-frame
    unique_id = uuid4().hex
    newtask = deepcopy(BatchTemplates.normal)
    newtask.seed = random.randint(LAUNCH_ARGS.min_seed, LAUNCH_ARGS.max_seed)
    newtask.uid = unique_id
    newtask.prompt = prompt
    newtask.performance_selection = Performance.LIGHTNING
    imgProcessor.generation_tasks.append(newtask)

    imgProcessor.process_all_tasks()
    

def check_processing():
    while imgProcessor.processing:
        log.info('Processing...')
        time.sleep(1.0)
    log.debug('Not processing.')
    return True


if __name__ == '__main__':
    # overwrites = OverWriteControls(overwrite_step=15)
    prompt = 'a cat in the forest, at night oil painting'
    prompt2 = 'a cat in the forest, at night oil painting'
    #generate_image(prompt)
    res = generate_image_to_stream(prompt)
    for r in res:
        print(r)
