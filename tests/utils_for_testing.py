import io
import random
import os

import random
import re
import time
import PIL
import PIL.Image
import dotenv

from uuid import uuid4

from typing import Generator

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # To solve the problem of importing modules from different directories
os.sys.path.insert(0,parentdir) 

from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from httpx import AsyncClient
from starlette.websockets import WebSocketDisconnect

from h3_utils.logging_util import LoggingUtil

from server.main import app

dotenv.load_dotenv()


test_client_main = TestClient(app)
test_client_secondary = TestClient(app)

async def async_client():
    async with AsyncClient(app=app) as client:
        yield client

def get_random_string(prefix: str = None, length: int = 3):
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result_str = ''.join(random.choice(letters) for i in range(length))
    return f"{prefix}_{result_str}" if prefix else result_str

def get_client_id():
    return random.randint(1000000000, 9999999999)

def get_uuid():
    return uuid4()

def get_mock_imagebytes(resolution: tuple = (1080, 1920)) -> io.BytesIO:
    image = PIL.Image.new("RGB", resolution)
    return image.tobytes()

    



