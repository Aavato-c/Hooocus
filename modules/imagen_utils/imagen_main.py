import os, sys

from consts import SHOULD_LOG_PERFORMANCE
from unavoided_globals import global_model_management, img_processor_globlal

currdir = os.path.abspath(__file__)
sys.path.append(currdir.split("Hooocus")[0] + "Hooocus")

import base64
import io
import json
import cv2
from numpy import ndarray
from db import crud
from db.database import get_db, get_db_inmem, get_db_unmanaged
from db.models.pydantic_m import GenerationStates
from modules.async_worker import ImageTaskProcessor
from contextlib import nullcontext
from unavoided_globals.img_processor_globlal import create_image_processor

from PIL import Image, ImageDraw, ImageFont
from h3_utils.logging_util import LoggingUtil, PerfLogger
import time
from h3_utils.config import ImageGenerationObject, DefaultConfigImageGen
from h3_utils.flags import OUTPUTFORMAT_LIT, OutputFormat, RETURN_FORMATS

from cProfile import Profile
from pstats import SortKey, Stats

log = LoggingUtil(__name__).get_logger()
perflog = PerfLogger("perflog").get_logger()


# TODO - Is this necessary?

DEBUG_IMAGEN = False

if DEBUG_IMAGEN:
    log.warning("Debug mode enabled in imagen_main.py.")

log.info("In imagen_main.py")


def _generate_image_with_text(prompt: str) -> bool:
    # For generating image bytearrays for sending visual information

    # Generate image
    img = Image.new("RGB", (640, 480), color=(0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default().font_variant(size=60)
    d.text((30, 220), prompt, fill=(255, 255, 255), align="center", font=font)

    # Convert to byte array
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="WEBP")
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


not_ready_arr_1 = _generate_image_with_text("Waiting to start.")
not_ready_arr_2 = _generate_image_with_text("Waiting to start..")
not_ready_arr_3 = _generate_image_with_text("Waiting to start...")
notreadys = [not_ready_arr_1, not_ready_arr_2, not_ready_arr_3]


def encoded_image_helper(
    image: ndarray,
    format: RETURN_FORMATS.LIT,
    yield_type: str,
    img_format: str = OUTPUTFORMAT_LIT,
) -> bytes:
    if yield_type == "finish":
        return b"--frame--\r\n"

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    match img_format:
        case OutputFormat.WEBP:
            (flag, encodedImage) = cv2.imencode(".webp", rgb_image)
        case OutputFormat.PNG:
            (flag, encodedImage) = cv2.imencode(".png", rgb_image)
        case OutputFormat.JPEG:
            (flag, encodedImage) = cv2.imencode(".jpeg", rgb_image)
        case _:
            raise Exception("Invalid image format.")
    if not flag:
        raise Exception("Error encoding image.")

    match format:
        # '<img src="data:image/webp;base64,{base64.b64encode(encodedImage).decode("utf-8")}" />'.encode()
        case RETURN_FORMATS.json:
            return (
                b"--frame\r\n"
                b"Content-Type: application/json\r\n\r\n"
                + json.dumps(
                    {
                        "type": yield_type,
                        "image": base64.b64encode(encodedImage).decode("utf-8"),
                    }
                ).encode()
                + b"\r\n"
            )
        case RETURN_FORMATS.image:
            return (
                b"--frame\r\n"
                b"Content-Type: image/"
                + img_format.encode()
                + b"\r\n\r\n"
                + bytearray(encodedImage)
                + b"\r\n"
            )
        case RETURN_FORMATS.src_for_img_as_html:
            return (
                b"--frame\r\n"
                b"Content-Encoding: base64\r\n"
                b"Content-Type: image/"
                + img_format.encode()
                + b"\r\n\r\n"
                + base64.b64encode(encodedImage)
                + b"\r\n"
            )

        case RETURN_FORMATS.src_for_img_as_json:
            return (
                b"--frame\r\n"
                b"Content-Type: application/json\r\n\r\n"
                + json.dumps(
                    {
                        "type": yield_type,
                        "image": b"data:image/"
                        + img_format.encode()
                        + b";base64,"
                        + base64.b64encode(encodedImage)
                        + b"",
                    }
                ).encode()
                + b"\r\n"
            )
        case _:
            raise Exception("Invalid format.")


def img_convert_from_generations(image: ndarray, img_format: str = "webp") -> bytes:
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    match img_format:
        case "webp":
            (flag, encodedImage) = cv2.imencode(".webp", rgb_image)
        case "png":
            (flag, encodedImage) = cv2.imencode(".png", rgb_image)
        case "jpeg":
            (flag, encodedImage) = cv2.imencode(".jpeg", rgb_image)
        case _:
            raise Exception("Invalid image format.")
    if not flag:
        raise Exception("Error encoding image.")

    return bytearray(encodedImage)


def generate_image_to_stream(
    seed_generation_task: dict | object,
    unique_id: str,
    img_format: str = OutputFormat.WEBP,
    return_format: RETURN_FORMATS.LIT = RETURN_FORMATS.image,
    result_return_format: RETURN_FORMATS.LIT = RETURN_FORMATS.image,
):

    # https://stackoverflow.com/questions/65971081/streaming-video-from-camera-in-fastapi-results-in-frozen-image-after-first-frame
    # About multi part: https://en.wikipedia.org/wiki/MIME#Multipart_messages

    contextmanager_if_perf = Profile if SHOULD_LOG_PERFORMANCE else nullcontext
    with contextmanager_if_perf() as pr:
        from unavoided_globals.shared import IMAGE_PROCESSOR as imgProcessor

        imgProcessor: ImageTaskProcessor
        if not imgProcessor:
            # GLOBAL VAR USAGE
            create_image_processor()
            from unavoided_globals.shared import IMAGE_PROCESSOR as imgProcessor

            if not imgProcessor:
                raise Exception("Image processor not created.")

        normal_template = DefaultConfigImageGen
        gentask = json.loads(seed_generation_task.generation_data)
        newtask = ImageGenerationObject(**gentask)
        if newtask.uid != unique_id:
            newtask.uid = unique_id

        # newtask.overwrite_controls = OverWriteControls(overwrite_step=12)
        final_task = normal_template.model_copy(update=newtask.model_dump())
        imgProcessor.generation_tasks.append(final_task)
        finished = False
        max_waits = 100

        iterations = 0

        if newtask.image_number > 1:
            raise Exception("Image number must be 1.")

        log.debug("In generate_image_to_stream. Starting to yield images.")
        try:
            inmem_db = get_db_inmem()
            db = get_db_unmanaged()
            while not finished:
                iterations += 1
                if max_waits <= 0:
                    raise Exception("Max waits reached.")
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
                            log.info("Processing...")
                            time.sleep(1.0)
                            continue
                        else:
                            log.error("No image processing.")
                            raise e
                    except Exception as e:
                        raise e

                    match img_res.yield_type:

                        case "starting":
                            log.debug("Got starting.")
                            time.sleep(0.2)

                        case "preview":
                            log.debug("Got preview.")
                            converted_img = img_convert_from_generations(img_res.image)

                            if not crud.update_inmem_img_cache(
                                inmem_db, unique_id, converted_img, img_format
                            ):
                                raise Exception("Error updating in-memory image cache.")

                            crud.update_imageorder_status(
                                db, unique_id, GenerationStates.IN_PROGRESS
                            )
                            log.debug("Updated inmem cache.")
                            yieldable = encoded_image_helper(
                                img_res.image, return_format, "preview", img_format
                            )
                            yield yieldable

                        case "result":
                            log.debug("Got result.")
                            converted_img = img_convert_from_generations(img_res.image)

                            if not crud.update_inmem_img_cache(
                                inmem_db, unique_id, converted_img, img_format
                            ):
                                raise Exception(
                                    "Error updating in-memory image cache with final img."
                                )

                            yieldable = encoded_image_helper(
                                img_res.image,
                                result_return_format,
                                "result",
                                img_format,
                            )
                            yield yieldable

                        case "uri":
                            log.debug("Got uri.")
                            crud.update_imageorder_status(
                                db,
                                unique_id,
                                GenerationStates.COMPLETED,
                                img_res.message,
                            )

                        case "finish":
                            log.debug("Got finish.")
                            finished = True
                            yieldable = encoded_image_helper(
                                img_res.image, return_format, "finish", img_format
                            )
                            crud.clear_cache_for_temp_img(inmem_db, unique_id)
                            if SHOULD_LOG_PERFORMANCE:
                                stats_str = io.StringIO()
                                stats = (
                                    Stats(pr, stream=stats_str)
                                    .sort_stats(SortKey.CALLS)
                                    .print_stats()
                                )
                                perflog.info(stats_str.getvalue())
                            yield yieldable

                        case "waiting":
                            iteration_image = iterations % 3
                            yield notreadys[iteration_image]
                            time.sleep(0.2)

                        case _:
                            raise Exception("Invalid yield type.")

                else:
                    if imgProcessor.processing:
                        max_waits -= 1
                        time.sleep(1)
                        continue
        finally:
            log.info("Closing inmem_db and db.")
            if not finished:
                # TODO Remove if not raised
                db.close()
                raise Exception("Not finished but ready to close?")

            inmem_db.close()
            db.close()


def yield_temps_if_streaming(
    unique_id: str,
):
    finished = False
    final_yielded = False
    max_waits = 100
    iterations = 0
    inmem_db = get_db_inmem()
    db = get_db_unmanaged()
    log.debug("Starting to yield temps.")
    try:
        while not finished:
            iterations += 1
            if max_waits <= 0:
                raise Exception("Max waits reached.")
            time.sleep(0.2)

            temp_status = crud.should_generate_or_url(db, unique_id)
            log.debug(f"Temp status: {temp_status}")
            if iterations > 100:
                log.error(f"Iterations exceeded in temp yilder: {iterations}")
                final_yielded = True
                crud.modify_process_state(db, unique_id, GenerationStates.NOT_STARTED)
                global_model_management.global_model_management.interrupt_current_processing()

            if final_yielded == True:
                log.debug("In temp yield: Got final yield.")
                yield (b"--frame--\r\n")
                finished = True
                continue

            match temp_status:
                case GenerationStates.COMPLETED:
                    log.debug("Yielded completed image.")
                    tempimg, imgformat = crud.get_temp_img_for_order(
                        inmem_db, unique_id
                    )
                    log.debug("Yielded final image.")
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/"
                        + imgformat.encode()
                        + b"\r\n\r\n"
                        + tempimg
                        + b"\r\n"
                    )
                    final_yielded = True

                case GenerationStates.IN_PROGRESS:
                    log.debug("In temp yield: Got in progress.")
                    tempimg, imgformat = crud.get_temp_img_for_order(
                        inmem_db, unique_id
                    )
                    log.debug("Yielded in progress image.")
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/"
                        + imgformat.encode()
                        + b"\r\n\r\n"
                        + tempimg
                        + b"\r\n"
                    )

                case GenerationStates.STARTING:
                    log.debug("In temp yield: Got starting.")
                    iteration_image = iterations % 3
                    log.debug("Yielded starting image.")
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/webp\r\n\r\n"
                        + notreadys[iteration_image]
                        + b"\r\n"
                    )

                case _:
                    raise Exception("Invalid generation state.")
    except Exception as e:
        log.error(f"Error in temp yield: {e}")
        db.close()
        inmem_db.close()

    finally:
        log.debug("Closing inmem_db and db in Temp Yield.")
        inmem_db.close()
        db.close()


if __name__ == "__main__":
    # overwrites = OverWriteControls(overwrite_step=15)
    prompt = "a cat in the forest, at night oil painting"
    # generate_image(prompt)
    new_gentask = ImageGenerationObject(prompt=prompt)
    db = get_db_unmanaged()
    new_id = crud.add_imageorder(db, new_gentask)
    db.close()
    res = generate_image_to_stream(
        ImageGenerationObject(prompt=prompt),
        new_id,
        img_format="webp",
        return_format="json",
    )
    for r in res:
        log.debug(r)
