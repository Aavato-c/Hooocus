
import os
import sys
from typing import Annotated
from uuid import uuid4
import uvicorn

from h3_utils.path_configs import FolderPathsConfig
from server.auth_handlers import verify_user
ROOT_DIR = os.path.abspath(__file__).split("server")[0]
sys.path.append(ROOT_DIR)

from sqlalchemy.orm import Session

from fastapi import FastAPI, HTTPException, Response, Depends
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse

from db.database import get_db
from db import crud

from imagen_main import generate_image_to_stream

from h3_utils.logging_util import LoggingUtil
from h3_utils.config import ImageGenerationObject

from unavoided_globals import img_processor_globlal, shared

log = LoggingUtil(name="main.py").get_logger()


ags = sys.argv
if len(ags) > 1:
    GUNICORN_ID = ags[1]
    
app = FastAPI()

SERVER_URL = os.environ.get("SERVER_URL", None)

if SERVER_URL is None:
    log.error("SERVER_URL is not set.")
    exit(1)

@app.get("/")
def read_root():
    return JSONResponse(content="Hello World", status_code=200)

@app.get("/{file_uuid}.{extension}")
def serve_photo(file_uuid: str, extension: str, db: Session = Depends(get_db)):
    try:
        gen_status = crud.should_generate_or_url(file_uuid)
        match gen_status:
            
            case "generate":
                order_data = crud.get_imageorder(db, file_uuid)
                if order_data is None:
                    return JSONResponse(content="", status_code=404)
                StreamingResponse(generate_image_to_stream(order_data, file_uuid), media_type="multipart/x-mixed-replace; boundary=frame")
            
            case "url":
                if os.path.exists(f"{FolderPathsConfig.path_outputs}/{file_uuid}.{extension}"):
                    with open(f"outputs/{file_uuid}.{extension}", "rb") as f:
                        photo = f.read()
                    return Response(content=photo, media_type=f"image/{extension}")
                else:
                    raise HTTPException(status_code=500)
            
            case "not_found":
                return JSONResponse(status_code=404)
        
    except Exception as e:
        log.error(f"Error serving photo: {e}")
        return JSONResponse(status_code=500)
    
@app.post("/gen/photo/normal")
def get_photo_genobject(_is_verified: Annotated[bool, Depends(verify_user)], request: dict, db: Session = Depends(get_db)):
    try:
        request_validated = ImageGenerationObject.model_validate(request)
        uuid_of_order = crud.add_imageorder(db, request_validated)
        return RedirectResponse(url=f"{SERVER_URL}/{uuid_of_order}.webp")
    except Exception as e:
        log.error(f"Error adding image order: {e}")
        return JSONResponse(status_code=500)



def main_entry(process_uuid = None, max_processes = 1):
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
    uvicorn.run(app)
