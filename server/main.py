
import os
import sys
from typing import Annotated
from uuid import uuid4
import uvicorn

from server.auth_handlers import verify_user
ROOT_DIR = os.path.abspath(__file__).split("server")[0]
sys.path.append(ROOT_DIR)

from sqlalchemy.orm import Session

from fastapi import FastAPI, Response, Depends
from fastapi.responses import JSONResponse, StreamingResponse

from db.database import get_db

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

@app.get("/{filename}.{extension}")
def serve_photo(filename: str, extension: str):
    try:
        if os.path.exists(f"outputs/{filename}.{extension}") is False:
            return JSONResponse(content="File not found.", status_code=404)
        with open(f"outputs/{filename}.{extension}", "rb") as f:
            photo = f.read()
            return Response(content=photo, media_type=f"image/{extension}")
        
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)
    
@app.post("/getphoto")
def get_photo_genobject(_is_verified: Annotated[bool, Depends(verify_user)], request: dict, db: Session = Depends(get_db)):
    try:
        new_id = uuid4().hex
        request_validated = ImageGenerationObject.model_validate(request)
        prompt = request_validated.prompt
        # Todo handle input image urls here
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)
    try:
        return StreamingResponse(generate_image_to_stream(request_validated, new_id), media_type="multipart/x-mixed-replace; boundary=frame")
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)
    finally:
        pass

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
