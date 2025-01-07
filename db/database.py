import os, sys

import consts
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURR_DIR.split("db")[0])

from consts import DB_URL, DB_URL_TEST
from h3_utils.logging_util import LoggingUtil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models.sqlalchemy_m import Base
import db.models.inmem_db_models as inmemModels



logger = LoggingUtil(__name__).get_logger()

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

in_mem_url = "sqlite:////run/shm/inmem.db"

in_memory_engine = create_engine(DB_URL, connect_args={"check_same_thread": False})


# Create a session object that will be used to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

InMemSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=in_memory_engine)

# Create the database tables
Base.metadata.create_all(bind=engine)

inmemModels.InMemBase.metadata.create_all(bind=in_memory_engine)


def get_db():
    """Get database connection object that can be used to interact with the database.
    It is a generator function that will automatically close the connection after the operation is done.
    The connection object is used to interact with the database in crud.py.

    Args:
        None

    Yields:
        db: database connection object

    Finally:
        db.close(): close the database

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_unmanaged():
    # GLOBAL VAR OBSERVATION
    if consts.TESTING == True:
        engine_test = create_engine(DB_URL_TEST, connect_args={"check_same_thread": False})
        SessionLocalTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)
        db = SessionLocalTesting()
    else:
        db = SessionLocal()
    return db


def get_db_inmem():
    db = InMemSessionLocal()
    return db

def get_temp_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()