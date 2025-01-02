import base64
from copy import deepcopy
import datetime
import io
from operator import not_
import os
import random
from uuid import uuid4
import cv2
from fastapi.responses import HTMLResponse
from numpy import ndarray
from regex import E, F
from torch import seed
from h3_utils.flags import Performance
from h3_utils.launch.launch import prepare_environment
from modules.async_worker import ImageTaskProcessor
prepare_environment()

from PIL import Image, ImageDraw, ImageFont
from h3_utils.logging_util import LoggingUtil
import time
from h3_utils.config import LAUNCH_ARGS, ImageGenerationObject, OverWriteControls, YieldObject
from h3_utils.img_processor_globlal import imgProcessor, BatchTemplates

log = LoggingUtil(name="imagen_main.py").get_logger()

DEBUG_IMAGEN = False

OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'outputs')




def _generate_image_with_text(prompt: str) -> bool:
    # For generating image bytearrays for sending visual information

    # Generate image
    img = Image.new('RGB', (640, 480), color = (0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default().font_variant(size=60)
    d.text((30,220), prompt, fill=(255,255,255), align='center', font=font)

    # Convert to byte array
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='WEBP')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr




not_ready_arr_1 = _generate_image_with_text('Waiting to start.')
not_ready_arr_2 = _generate_image_with_text('Waiting to start..')
not_ready_arr_3 = _generate_image_with_text('Waiting to start...')
notreadys = [not_ready_arr_1, not_ready_arr_2, not_ready_arr_3]


def generate_image_to_stream_using_prompt(prompt: str):
    # https://stackoverflow.com/questions/65971081/streaming-video-from-camera-in-fastapi-results-in-frozen-image-after-first-frame
    # About multi part: https://en.wikipedia.org/wiki/MIME#Multipart_messages
    unique_id = uuid4().hex
    newtask = deepcopy(BatchTemplates.normal)
    newtask.seed = random.randint(LAUNCH_ARGS.min_seed, LAUNCH_ARGS.max_seed)
    newtask.uid = unique_id
    newtask.adaptive_cfg = 4
    newtask.cfg_scale = 2.0
    #newtask.overwrite_controls = OverWriteControls(overwrite_step=12)
    newtask.prompt = prompt
    newtask.sample_sharpness = 8.5
    log.info(f"Using seed: {newtask.seed}\nadaptive_cfg: {newtask.adaptive_cfg}\ncfg_scale: {newtask.cfg_scale}\nprompt: {newtask.prompt}\nsample_sharpness: {newtask.sample_sharpness}")


    imgProcessor.generation_tasks.append(newtask)
    
    finished = False
    notready_iter = 0
    max_loops = 1000
    while not finished:
        max_loops -= 1
        if max_loops <= 0:
            raise Exception('Max loops reached.')
        time.sleep(1.0)
        if len(imgProcessor.yields) > 0:
            try:
                img_res = imgProcessor.yields[unique_id].pop(0)
            except Exception as e:
                log.error(f"Couldn't subscribe to image processing. {str(e)}")
                time.sleep(0.05)
                continue
            img_res: YieldObject
            if img_res.yield_type == "preview" and img_res.uid == unique_id:
                rgb_image = cv2.cvtColor(img_res.image, cv2.COLOR_BGR2RGB)
                (flag, encodedImage) = cv2.imencode(".webp", rgb_image)
                if not flag:
                    continue
                else:
                    log.debug('Image preview generated.')
                    if not DEBUG_IMAGEN:
                        yield (b'--frame\r\n' b'Content-Type: image/webp\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
                        # yield (b'--frame\r\n' b'Content-Type: text/html\r\n\r\n' + img_res.url + b'\r\n' + b'--frame--\r\n')
                        # finished = True
                    else:
                        yield f"Image preview generated: {max_loops}"
                
                """     elif img_res.yield_type == "result" and img_res.uid == unique_id:
                rgb_image = cv2.cvtColor(img_res.image, cv2.COLOR_BGR2RGB)
                (flag, encodedImage) = cv2.imencode(".webp", rgb_image)
                if not flag:
                    raise Exception('Error encoding image.')
                else:
                    log.debug('Image result generated.')
                    finished = True
                    if not DEBUG_IMAGEN:
                        yield (b'--frame\r\n' b'Content-Type: image/webp\r\n\r\n' + bytearray(encodedImage) + b'\r\n' + b'--frame--\r\n')
                    else:
                        pass """

            elif img_res.yield_type == "redirect_url" and img_res.uid == unique_id:
                log.debug('Redirecting to URL.')
                log.info(f"URL for a ready img: {img_res.url}")
                finished = True
                yield (b'--frame\r\n' b'Content-Type: text/html\r\n\r\n' + img_res.url + b'\r\n' + b'--frame--\r\n')

            else:
                if img_res.uid == unique_id:
                    log.debug('Image not ready.')
                    log.info(f"Image not ready. {img_res}")
                else:
                    notready_iter += 1
                    photo_chosen = notreadys[notready_iter % 3]
                    yield (b'--frame\r\n' b'Content-Type: image/webp\r\n\r\n' + photo_chosen + b'\r\n')


def generate_image_to_stream(seed_generation_task: ImageGenerationObject):
    unique_id = uuid4().hex
    
    try:
        newtask = ImageGenerationObject.model_validate(seed_generation_task)
    except Exception as e:
        log.error(str(e))
        raise Exception('Error validating request.')
    
    newtask.seed = random.randint(LAUNCH_ARGS.min_seed, LAUNCH_ARGS.max_seed)
    newtask.uid = unique_id
    imgProcessor.generation_tasks.append(newtask)
    
    finished = False
    notready_iter = 0
    max_loops = 1000
    while not finished:
        max_loops -= 1
        if max_loops <= 0:
            raise Exception('Max loops reached.')
        time.sleep(0.49)
        if unique_id in imgProcessor.yields:
            if len(imgProcessor.yields[unique_id]) > 0:
                try:
                    img_res = imgProcessor.yields[unique_id].pop(0)
                except Exception as e:
                    time.sleep(0.05)
                    continue
                img_res: YieldObject
                if img_res.yield_type == "preview" and img_res.uid == unique_id:
                    rgb_image = cv2.cvtColor(img_res.image, cv2.COLOR_BGR2RGB)
                    (flag, encodedImage) = cv2.imencode(".webp", rgb_image)
                    if not flag:
                        continue
                    else:
                        log.debug('Image preview generated.')
                        if not DEBUG_IMAGEN:
                            yield (b'--frame\r\n' b'Content-Type: image/webp\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
                        else:
                            yield f"Image preview generated: {max_loops}"
                elif img_res.yield_type == "result" and img_res.uid == unique_id:
                    rgb_image = cv2.cvtColor(img_res.image, cv2.COLOR_BGR2RGB)
                    (flag, encodedImage) = cv2.imencode(".webp", rgb_image)
                    if not flag:
                        raise Exception('Error encoding image.')
                    else:
                        log.debug('Image result generated.')
                        finished = True
                        if not DEBUG_IMAGEN:
                            yield (b'--frame\r\n' b'Content-Type: image/webp\r\n\r\n' + bytearray(encodedImage) + b'\r\n' + b'--frame--\r\n')
                        else:
                            pass

                elif img_res.yield_type == "redirect_url" and img_res.uid == unique_id:
                    log.debug('Redirecting to URL.')
                    finished = True
                    yield (b'--frame\r\n' b'Content-Type: text/html\r\n\r\n' + img_res.url + b'\r\n' + b'--frame--\r\n')

                else:
                    if img_res[-1] == unique_id:
                        log.debug('Image not ready.')
                    else:
                        notready_iter += 1
                        photo_chosen = notreadys[notready_iter % 3]
                        yield (b'--frame\r\n' b'Content-Type: image/webp\r\n\r\n' + photo_chosen + b'\r\n')
        else:
            log.debug('Image processing not started.')
            notready_iter += 1
            photo_chosen = notreadys[notready_iter % 3]
            yield (b'--frame\r\n' b'Content-Type: image/webp\r\n\r\n' + photo_chosen + b'\r\n')

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
