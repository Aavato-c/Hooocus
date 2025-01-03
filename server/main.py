
import os
import sys
from uuid import uuid4

ROOT_DIR = os.path.abspath(__file__).split("server")[0]
sys.path.append(ROOT_DIR)
from h3_utils.config import ImageGenerationObject
from unavoided_globals import img_processor_globlal


from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse, StreamingResponse
from imagen_main import generate_image_to_stream, generate_image_to_stream_using_prompt
import uvicorn
from h3_utils.logging_util import LoggingUtil
import unavoided_globals.shared as shared

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

@app.get("/photo/{filename}.{extension}")
def serve_photo(filename: str, extension: str):
    try:
        if os.path.exists(f"outputs/{filename}.{extension}") is False:
            return JSONResponse(content="File not found.", status_code=404)
        with open(f"outputs/{filename}.{extension}", "rb") as f:
            photo = f.read()
            return Response(content=photo, media_type=f"image/{extension}")
        
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)
    

@app.get("/getphoto/{prompt}.webp")
def get_photo_prompt(prompt: str):
    new_id = uuid4().hex
    try:
        prompt = prompt.replace("_", " ")
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)
    # We'll generate a lot of <img> tags
    return StreamingResponse(generate_image_to_stream_using_prompt(prompt, unique_id=new_id), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/getphoto")
def get_photo_genobject(request: dict):
    try:
        new_id = uuid4().hex
        request_validated = ImageGenerationObject.model_validate(request)
        prompt = request_validated.prompt
        # Todo handle input image urls here
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)
    # We'll generate a lot of <img> tags
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
