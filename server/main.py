import json
import os
import sys

from h3_utils.config import ImageGenerationObject

ROOT_DIR = os.path.abspath(__file__).split("server")[0]
sys.path.append(ROOT_DIR)

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse, StreamingResponse
from imagen_main import generate_image_to_stream, generate_image_to_stream_using_prompt
import uvicorn
from h3_utils.logging_util import LoggingUtil

log = LoggingUtil(name="main.py").get_logger()

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
    try:
        prompt = prompt.replace("_", " ")
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)
    # We'll generate a lot of <img> tags
    return StreamingResponse(generate_image_to_stream_using_prompt(prompt), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/getphoto")
def get_photo_genobject(request: ImageGenerationObject):
    try:
        prompt = request.prompt    
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)
    # We'll generate a lot of <img> tags
    return StreamingResponse(generate_image_to_stream(request), media_type="multipart/x-mixed-replace; boundary=frame")



def main_entry():
    uvicorn.run(app)
    pass

if __name__ == "__main__":
    main_entry()