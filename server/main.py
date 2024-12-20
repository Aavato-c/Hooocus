import os
import sys

ROOT_DIR = os.path.abspath(__file__).split("server")[0]
sys.path.append(ROOT_DIR)

from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from imagen_main import generate_image_to_stream
import uvicorn
from h3_utils.logging_util import LoggingUtil
log = LoggingUtil(name="main.py").get_logger()

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
    # We'll generate a lot of <img> tags
    return StreamingResponse(generate_image_to_stream(prompt), media_type="multipart/x-mixed-replace; boundary=frame")



def main_entry():
    uvicorn.run(app)
    pass

if __name__ == "__main__":
    main_entry()