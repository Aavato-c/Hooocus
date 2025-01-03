import base64
from copy import deepcopy
import datetime
import io
import json
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
from h3_utils.config import LAUNCH_ARGS, BatchTemplates, ImageGenerationObject, OverWriteControls, YieldObject

log = LoggingUtil(name="imagen_main.py").get_logger()

DEBUG_IMAGEN = False

if DEBUG_IMAGEN:
    log.warning('Debug mode enabled in imagen_main.py.')

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


def generate_image_to_stream_using_prompt(prompt: str, unique_id: str):
    # https://stackoverflow.com/questions/65971081/streaming-video-from-camera-in-fastapi-results-in-frozen-image-after-first-frame
    # About multi part: https://en.wikipedia.org/wiki/MIME#Multipart_messages
    from unavoided_globals.shared import IMAGE_PROCESSOR as imgProcessor
    if not imgProcessor:
        log.error('No image processor.')
        raise Exception('No image processor.')
    newtask = deepcopy(BatchTemplates.normal)
    newtask.seed = random.randint(LAUNCH_ARGS.min_seed, LAUNCH_ARGS.max_seed)
    newtask.uid = unique_id
    newtask.adaptive_cfg = 4
    newtask.cfg_scale = 2.0
    #newtask.overwrite_controls = OverWriteControls(overwrite_step=12)
    newtask.prompt = prompt
    newtask.sample_sharpness = 8.5
    log.info(f"Using seed: {newtask.seed}\nadaptive_cfg: {newtask.adaptive_cfg}\ncfg_scale: {newtask.cfg_scale}\nprompt: {newtask.prompt}\nsample_sharpness: {newtask.sample_sharpness}")

    
    finished = False
    notready_iter = 0
    max_waits = 100
    while not finished:

        if max_waits <= 0:
            raise Exception('Max waits reached.')
        time.sleep(1.0)
        if len(imgProcessor.yields) > 0:
            try:
                if len(imgProcessor.yields[unique_id]) == 0:
                    max_waits -= 1
                    time.sleep(1)
                    continue
                img_res = imgProcessor.yields[unique_id].pop(0)
            except KeyError as e:
                if imgProcessor.processing:
                    log.info('Processing...')
                    time.sleep(1.0)
                    continue
                else:
                    log.error('No image processing.')
                    raise e
            except Exception as e:
                raise e
            
            img_res: YieldObject
            if img_res.yield_type == "preview" and img_res.uid == unique_id:
                rgb_image = cv2.cvtColor(img_res.image, cv2.COLOR_BGR2RGB)
                (flag, encodedImage) = cv2.imencode(".webp", rgb_image)
                if not flag:
                    continue
                else:
                    sent_first = True
                    log.debug('Image preview generated.')
                    if not DEBUG_IMAGEN:
                        yield (b'--frame\r\n' b'Content-Type: image/webp\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
                    else:
                        yield (b'--frame\r\n' b'Content-Type: text/html\r\n\r\n' + b'PREVIEW' + b'\r\n')
                

            elif img_res.yield_type == "redirect_image" and img_res.uid == unique_id:
                log.info(f"URL for a ready img: {img_res.url}")
                sent_first = True
                url_of_image = img_res.url
                continue

            elif img_res.yield_type == "result_in_callback":
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
                log.error(f"Unhandeled yield type: {img_res.yield_type}")

        else:
            log.info('In a loop.')
            notready_iter += 1
            photo_chosen = notreadys[notready_iter % 3]
            if not DEBUG_IMAGEN:
                yield (b'--frame\r\n' b'Content-Type: image/webp\r\n\r\n' + photo_chosen + b'\r\n')
            else:
                yield (b'--frame\r\n' b'Content-Type: text/html\r\n\r\n' + b"NOT_READY" + b'\r\n')

def generate_image_to_stream(seed_generation_task: ImageGenerationObject, unique_id: str):
    # https://stackoverflow.com/questions/65971081/streaming-video-from-camera-in-fastapi-results-in-frozen-image-after-first-frame
    # About multi part: https://en.wikipedia.org/wiki/MIME#Multipart_messages
    normal_template = BatchTemplates.normal
    
    newtask = seed_generation_task
    newtask.seed = random.randint(LAUNCH_ARGS.min_seed, LAUNCH_ARGS.max_seed)
    newtask.uid = unique_id
    newtask.adaptive_cfg = 4
    newtask.cfg_scale = 2.0
    #newtask.overwrite_controls = OverWriteControls(overwrite_step=12)
    newtask.sample_sharpness = 8.5
    final_task = normal_template.model_copy(update=newtask)
    imgProcessor.generation_tasks.append(final_task)
    finished = False
    notready_iter = 0
    max_waits = 100
    
    if newtask.image_number > 1:
        raise Exception('Image number must be 1.')
    
    while not finished:
        if max_waits <= 0:
            raise Exception('Max waits reached.')
        time.sleep(1.0)
        
        if unique_id not in imgProcessor.yields:
            time.sleep(1)
            max_waits -= 1
            continue

        if len(imgProcessor.yields[unique_id]) > 0:
            try:
                if len(imgProcessor.yields[unique_id]) == 0:
                    max_waits -= 1
                    time.sleep(1)
                    continue
                img_res = imgProcessor.yields[unique_id].pop(0)
            except KeyError as e:
                if imgProcessor.processing:
                    log.info('Processing...')
                    time.sleep(1.0)
                    continue
                else:
                    log.error('No image processing.')
                    raise e
            except Exception as e:
                raise e
            
            img_res: YieldObject
            if img_res.yield_type == "preview" and img_res.uid == unique_id:
                rgb_image = cv2.cvtColor(img_res.image, cv2.COLOR_BGR2RGB)
                (flag, encodedImage) = cv2.imencode(".webp", rgb_image)
                if not flag:
                    continue
                else:
                    sent_first = True
                    log.debug('Image preview generated.')
                    yield (
                        b'--frame\r\n' 
                        b'Content-Type: application/json\r\n\r\n'
                        + json.dumps({
                            'type': 'preview',
                            'image': base64.b64encode(encodedImage).decode('utf-8'),
                            'url': "",
                        }).encode()
                        + b'\r\n'
                    )
                        
            elif img_res.yield_type == "redirect_image" and img_res.uid == unique_id:
                log.info(f"URL for a ready img: {img_res.url}")
                url_of_image = img_res.url
                yield (
                    b'--frame\r\n'
                    b'Content-Type: application/json\r\n\r\n'
                    + json.dumps({
                        'type': 'redirect_image',
                        'image': "",
                        'url': url_of_image,
                    }).encode()
                    + b'\r\n'
                    + b'--frame--\r\n'
                )
                break

            elif img_res.yield_type == "result":
                rgb_image = cv2.cvtColor(img_res.image, cv2.COLOR_BGR2RGB)
                (flag, encodedImage) = cv2.imencode(".webp", rgb_image)
                if not flag:
                    raise Exception('Error encoding image.')
                else:
                    log.debug('Image result generated.')
                    finished = True
                    if not DEBUG_IMAGEN:
                        yield (
                            b'--frame\r\n'
                            b'Content-Type: application/json\r\n\r\n'
                            + json.dumps({
                                'type': 'result',
                                'image': base64.b64encode(encodedImage).decode('utf-8'),
                                'url': "",
                            }).encode()
                            + b'\r\n'
                            + b'--frame--\r\n'
                        )
                
            elif img_res.yield_type == "result_in_callback":
                pass
                
            else:
                log.error(f"Unhandeled yield type: {img_res.yield_type}")

        else:
            log.info('In a loop.')
            pass

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
