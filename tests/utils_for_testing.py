import os, sys
import io
import random
import time
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURR_DIR.split("tests")[0])

import PIL
import PIL.Image
import dotenv

from uuid import uuid4

from fastapi.testclient import TestClient

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.decl_api import DeclarativeBase

import db.models.sqlalchemy_m as dbm
from db.database import get_db

from h3_utils.logging_util import LoggingUtil

from server.main import app

dotenv.load_dotenv()

log = LoggingUtil("Test_db_setup").get_logger()

DB_URL_TEST = os.environ.get("DB_URL_TEST")

Base: DeclarativeBase = dbm.Base

""" if FORMAT_TEST_DATABASE:
    try:
        master_engine = create_engine(DB_URL_MASTER).execution_options(isolation_level="AUTOCOMMIT")
        conn = master_engine.connect()
        log.info(f"Dropping test database {DB_NAME_TEST}")
        conn.execute(text(f'DROP DATABASE IF EXISTS {DB_NAME_TEST} WITH (FORCE)'))
        log.info(f"Creating test database {DB_NAME_TEST}")
        conn.execute(text(f'CREATE DATABASE {DB_NAME_TEST}'))
    finally:
        conn.close()
        master_engine.dispose()
        master_engine.clear_compiled_cache()
        time.sleep(10) """

main_engine = create_engine(DB_URL_TEST)
Base.metadata.create_all(bind=main_engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=main_engine)

def get_test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = get_test_db
test_client_main = TestClient(app)
test_client_secondary = TestClient(app)

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

    



