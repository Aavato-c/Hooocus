import time
import os
import sys

from numpy import ndarray


ROOT_DIR = os.path.abspath(__file__).split("server")[0]
sys.path.append(ROOT_DIR)

from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from imagen_main import generate_image_to_stream
import uvicorn
from PIL import Image

app = FastAPI()


@app.get("/")
def read_root():
    return JSONResponse(content="Hello World", status_code=200)
    

@app.get("/getphoto/{prompt}")
def main(prompt: str):
    try:
        prompt = prompt.replace("_", " ")
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)
    return StreamingResponse(generate_image_to_stream(prompt), media_type="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    uvicorn.run(app)
    pass