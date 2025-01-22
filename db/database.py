from contextlib import contextmanager
import os, sys
from typing import Generator
import typing_extensions

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURR_DIR.split("db")[0])

import consts
from consts import DB_URL, DB_URL_TEST
from h3_utils.logging_util import LoggingUtil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from db.models.sqlalchemy_m import Base



logger = LoggingUtil(__name__).get_logger()

engine = create_engine(DB_URL, pool_size=20, max_overflow=0, connect_args={"check_same_thread": False})

in_mem_url = "sqlite:////tmp/h3_inmem.db"

in_memory_engine = create_engine(DB_URL, pool_size=20, max_overflow=0, connect_args={"check_same_thread": False})


# Create a session object that will be used to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#InMemSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=in_memory_engine)

# Create the database tables
Base.metadata.create_all(bind=engine)

#inmemModels.InMemBase.metadata.create_all(bind=in_memory_engine)

if consts.TESTING == True:
    engine_test = create_engine(DB_URL_TEST, connect_args={"check_same_thread": False})
    SessionLocalTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)
else:
    SessionLocalTesting = None



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
    if consts.TESTING == True:
        db = SessionLocalTesting()
    else:
        db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




def get_db_unmanaged() -> Session:
    # GLOBAL VAR OBSERVATION
    if consts.TESTING == True:
        db = SessionLocalTesting()
    else:
        db = SessionLocal()
    return db


@typing_extensions.deprecated("No more db_inmen, using normal db")
def get_db_inmem():
    #db = InMemSessionLocal()
    if consts.TESTING == True:
        db = SessionLocalTesting()
    else:
        db = SessionLocal()
    return db
