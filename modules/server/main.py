import os
import sys

ROOT_DIR = os.path.abspath(__file__).split("modules")[0]
sys.path.append(ROOT_DIR)

from typing import Annotated
from uuid import uuid4
import uvicorn
from pprint import pprint as pp
import traceback

from modules.server.auth_handlers import verify_user
from unavoided_globals import img_processor_globlal, shared

from sqlalchemy.orm import Session

from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError

from db.models.pydantic_m import GenerationStates
from db.database import get_db, get_temp_db
from db import crud

from modules.imagen_utils.imagen_main import (
    generate_image_to_stream,
    yield_temps_if_streaming,
)

from consts import IMAGEN_BACKEND_PORT, IMAGEN_BACKEND_URL, SERVER_URL

from h3_utils.path_configs import FolderPathsConfig
from h3_utils.logging_util import LoggingUtil
from h3_utils.config import ImageGenerationObject, ImageGenerationObjectForRequests


log = LoggingUtil(__name__).get_logger()


app = FastAPI()

if IMAGEN_BACKEND_URL is None:
    log.error("SERVER_URL is not set.")
    exit(1)


@app.exception_handler(Exception)
def debug_exception_handler(request: Request, exc: Exception):
    log.error(f"Error: {exc}, {traceback.format_exc()}")


@app.get("/")
def read_root():
    return JSONResponse(content="Hello World", status_code=200)


@app.get("/photo/{file_uuid}.{extension}")
def serve_photo(
    file_uuid: str,
    extension: str,
    db: Session = Depends(get_db),
    db_temp: Session = Depends(get_temp_db),
):
    try:
        gen_status = crud.should_generate_or_url(db, file_uuid)
        match gen_status:

            case GenerationStates.NOT_STARTED:
                log.debug(f"Status in serve_photo: {gen_status}")
                order_data = crud.get_imageorder(db, file_uuid)
                if order_data is None:
                    return JSONResponse(content="", status_code=404)
                crud.update_imageorder_status(db, file_uuid, GenerationStates.STARTING)
                return StreamingResponse(
                    generate_image_to_stream(order_data, file_uuid),
                    media_type="multipart/x-mixed-replace; boundary=frame",
                )

            case GenerationStates.COMPLETED:
                log.debug(f"Status in serve_photo: {gen_status}")
                if os.path.exists(
                    f"{FolderPathsConfig.path_outputs}/{file_uuid}.{extension}"
                ):
                    with open(f"outputs/{file_uuid}.{extension}", "rb") as f:
                        photo = f.read()
                    return Response(content=photo, media_type=f"image/{extension}")
                else:
                    raise HTTPException(status_code=500)

            case GenerationStates.STARTING | GenerationStates.IN_PROGRESS:
                log.debug(f"Status in serve_photo: {gen_status}")
                return StreamingResponse(
                    yield_temps_if_streaming(file_uuid),
                    media_type="multipart/x-mixed-replace; boundary=frame",
                )

            case GenerationStates.NOT_FOUND:
                return JSONResponse(status_code=404, content="")

            case _:
                return HTTPException(status_code=500)

    except Exception as e:
        log.error(f"Error serving photo: {e}")
        return JSONResponse(status_code=500, content="")


auth_doc = {
    "parameters": [
        {
            "name": "Authorization",
            "in": "header",
            "required": True,
            "description": "Bearer token",
            "schema": {"type": "string"},
        }
    ]
}


@app.post("/photo", openapi_extra=auth_doc)
@app.post("/gen/photo/normal", openapi_extra=auth_doc)
def get_photo_genobject(
    _is_verified: Annotated[bool, Depends(verify_user)],
    request: ImageGenerationObjectForRequests,
    db: Session = Depends(get_db),
):
    try:
        request_validated = ImageGenerationObject.model_validate(request)
        log.debug(f"Adding image order: {request_validated.model_dump()}")

        if request_validated.uid != "":
            log.info(
                f"Adding image order with UID: {request_validated.uid}. UID was provided."
            )
            uuid_of_order = crud.add_imageorder(
                db, request_validated, request_validated.uid
            )
        else:
            log.debug(
                f"Adding image order: {request_validated.uid}. No UID was provided."
            )
            uuid_of_order = crud.add_imageorder(db, request_validated)
        return JSONResponse(
            content={
                "uuid": uuid_of_order,
                "url": f"{SERVER_URL}/photo/{uuid_of_order}.webp",
                "test_url": f"{IMAGEN_BACKEND_URL}:{IMAGEN_BACKEND_PORT}/photo/{uuid_of_order}.webp",
            },
            status_code=201,
        )
    except Exception as e:
        log.error(f"Error adding image order: {e}")
        return JSONResponse(status_code=500)


def main_entry(process_uuid=None, max_processes=4):
    if process_uuid == None:
        log.error("No entry value provided.")
        sys.exit(1)
    else:
        shared.GLOBAL_GUNICORN_ID = process_uuid
        shared.MAX_PROCESSES = max_processes
        img_processor_globlal.create_image_processor()
        return app


if __name__ == "__main__":
    app = main_entry("RANDOM_UUID")
    uvicorn.run(
        app, port=IMAGEN_BACKEND_PORT
    )  # uvicorn server.main:app --reload --port 8111
