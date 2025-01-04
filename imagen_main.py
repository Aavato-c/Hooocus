import base64
import io
import json
import os
import random
from typing import Literal
import cv2
from numpy import ndarray
from regex import R
from torch import seed
from db import crud
from db.database import get_db, get_db_unmanaged
from h3_utils.flags import Performance
from modules.async_worker import ImageTaskProcessor
from unavoided_globals.img_processor_globlal import create_image_processor

from PIL import Image, ImageDraw, ImageFont
from h3_utils.logging_util import LoggingUtil
import time
from h3_utils.config import LAUNCH_ARGS, BatchTemplates, ImageGenerationObject, OverWriteControls, YieldObject

log = LoggingUtil(name="imagen_main.py").get_logger()

# TODO - Is this necessary?

DEBUG_IMAGEN = False

if DEBUG_IMAGEN:
    log.warning('Debug mode enabled in imagen_main.py.')

OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'outputs')



class RETURN_FORMATS:
    json = "json"
    image = "image"
    src_for_img_as_html = "src_for_img_as_html"
    src_for_img_as_json = "src_for_img_as_json"

    LIT = Literal["json", "image", "src_for_img_as_html", "src_for_img_as_json"]


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


def encoded_image_helper(image: ndarray, format: RETURN_FORMATS.LIT, yield_type: str, img_format: str = "webp") -> bytes:
    if yield_type == "finish":
        return (
            b'--frame--\r\n'
        )
    
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    match img_format:
        case "webp":
            (flag, encodedImage) = cv2.imencode(".webp", rgb_image)
        case "png":
            (flag, encodedImage) = cv2.imencode(".png", rgb_image)
        case "jpeg":
            (flag, encodedImage) = cv2.imencode(".jpeg", rgb_image)
        case _:
            raise Exception('Invalid image format.')    
    if not flag:
        raise Exception('Error encoding image.')
        
    match format:
            # '<img src="data:image/webp;base64,{base64.b64encode(encodedImage).decode("utf-8")}" />'.encode()
        case RETURN_FORMATS.json:
            return (
                b'--frame\r\n' 
                b'Content-Type: application/json\r\n\r\n'
                + json.dumps({
                    'type': yield_type,
                    'image': base64.b64encode(encodedImage).decode('utf-8'),
                }).encode()
                + b'\r\n'
            )
        case RETURN_FORMATS.image:
            return (
                b'--frame\r\n'
                b'Content-Type: image/' + img_format.encode() + b'\r\n\r\n'
                + bytearray(encodedImage)
                + b'\r\n'
            )
        case RETURN_FORMATS.src_for_img_as_html:
            return (
                b'--frame\r\n'
                b'Content-Encoding: base64\r\n'
                b'Content-Type: image/' + img_format.encode() + b'\r\n\r\n'
                + base64.b64encode(encodedImage)
                + b'\r\n'
            )
        
        case RETURN_FORMATS.src_for_img_as_json:
            return (
                b'--frame\r\n'
                b'Content-Type: application/json\r\n\r\n'
                + json.dumps({
                    'type': yield_type,
                    'image': b'data:image/' + img_format.encode() + b';base64,' + base64.b64encode(encodedImage) + b'',
                }).encode()
                + b'\r\n'
            )
        case _:
            raise Exception('Invalid format.')


def generate_image_to_stream(
        seed_generation_task: dict | object,
        unique_id: str,
        img_format: str = "webp",
        return_format: RETURN_FORMATS.LIT = RETURN_FORMATS.image,
        result_return_format: RETURN_FORMATS.LIT = RETURN_FORMATS.image
        ):
    
    # https://stackoverflow.com/questions/65971081/streaming-video-from-camera-in-fastapi-results-in-frozen-image-after-first-frame
    # About multi part: https://en.wikipedia.org/wiki/MIME#Multipart_messages

    from unavoided_globals.shared import IMAGE_PROCESSOR as imgProcessor
    imgProcessor: ImageTaskProcessor
    if not imgProcessor:
        # GLOBAL VAR USAGE
        create_image_processor()
        from unavoided_globals.shared import IMAGE_PROCESSOR as imgProcessor
        if not imgProcessor:
            raise Exception('Image processor not created.')
        
    normal_template = BatchTemplates.normal
    gentask = json.loads(seed_generation_task.generation_data)
    newtask = ImageGenerationObject(**gentask)
    newtask.seed = random.randint(LAUNCH_ARGS.min_seed, LAUNCH_ARGS.max_seed)
    newtask.uid = unique_id
    newtask.adaptive_cfg = 4
    newtask.cfg_scale = 2.0
    #newtask.overwrite_controls = OverWriteControls(overwrite_step=12)
    newtask.sample_sharpness = 10.5
    final_task = normal_template.model_copy(update=newtask.model_dump())
    imgProcessor.generation_tasks.append(final_task)
    finished = False
    max_waits = 100

    iterations = 0
    
    if newtask.image_number > 1:
        raise Exception('Image number must be 1.')
    
    while not finished:
        iterations += 1
        if max_waits <= 0:
            raise Exception('Max waits reached.')
        time.sleep(0.2)
        
        if unique_id not in imgProcessor.yields:
            time.sleep(1)
            max_waits -= 1
            continue

        if len(imgProcessor.yields[unique_id]) > 0:
            try:
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
            
            match img_res.yield_type:

                case "preview":
                    yieldable = encoded_image_helper(img_res.image, return_format, "preview", img_format)
                    yield yieldable

                case "result":
                    yieldable = encoded_image_helper(img_res.image, result_return_format, "result", img_format)
                    yield yieldable

                case "uri":
                    db = get_db_unmanaged()
                    crud.update_imageorder_status(db, unique_id, True, img_res.message)
                    db.close()
                    continue

                case "finish":
                    finished = True
                    yieldable = encoded_image_helper(img_res.image, return_format, "finish", img_format)
                    yield yieldable
                    break

                case "waiting":
                    iteration_image = iterations % 3
                    yield notreadys[iteration_image]
                    time.sleep(0.2)

                case _:
                    raise Exception('Invalid yield type.')

        else:
            if imgProcessor.processing:
                    max_waits -= 1
                    time.sleep(1)
                    continue


if __name__ == '__main__':
    # overwrites = OverWriteControls(overwrite_step=15)
    prompt = 'a cat in the forest, at night oil painting'
    #generate_image(prompt)
    new_gentask = ImageGenerationObject(prompt=prompt)
    db = get_db_unmanaged()
    new_id = crud.add_imageorder(db, new_gentask)
    db.close()
    res = generate_image_to_stream(ImageGenerationObject(prompt=prompt), new_id, img_format='webp', return_format='json')
    for r in res:
        log.debug(r)
