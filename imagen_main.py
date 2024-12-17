import concurrent.futures
import io
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
from h3_utils.config import ImageGenerationObject, OverWriteControls, DefaultConfigImageGen
from unavoided_globals.global_model_management import global_model_management
from PIL import Image
from h3_utils.logging_util import LoggingUtil
log = LoggingUtil().get_logger()
import time

imgProcessor = ImageTaskProcessor()

class BatchTemplates:
    _shared = DefaultConfigImageGen
    _shared.image_number = 1

    normal = ImageGenerationObject(
        cfg_scale=15.0,
        sample_sharpness=15.0,
        )



def generate_image_to_stream(prompt: str):
    # https://stackoverflow.com/questions/65971081/streaming-video-from-camera-in-fastapi-results-in-frozen-image-after-first-frame
    unique_id = uuid4().hex
    newtask = deepcopy(BatchTemplates.normal)
    newtask.uid = unique_id
    newtask.prompt = prompt
    imgProcessor.generation_tasks.append(newtask)

    # Create and run task asynchronously
    concurrent.futures.ThreadPoolExecutor().submit(imgProcessor.process_all_tasks)
    
    finished = False
    max_loops = 100
    while not finished:
        if max_loops == 0:
            log.error('Max loops reached.')
            break
        max_loops -= 1
        time.sleep(1.01)
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

                



def generate_image(task: ImageGenerationObject):

    try:
        with global_model_management.interrupt_processing_mutex:
            global_model_management.interrupt_processing = False
        
            print(task.refiner_model)
            imgProcessor = ImageTaskProcessor()
            imgProcessor.generation_tasks.append(task)
            finished = False

            time.sleep(0.01)
            imgProcessor.process_all_tasks()
            print('Image generation finished.')
            ...

    except Exception as e:
        print(str(e))

    finally:
        print('Done')

overwrites = OverWriteControls(overwrite_step=15)

if __name__ == '__main__':
    image_params = ImageGenerationObject(
        prompt="A car without headlights a banana",
        performance_selection=Performance.SPEED,
        overwrite_controls=overwrites,
        )
    
    generate_image(image_params)
    
    print('Done fom main.py')