import os, sys

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURR_DIR.split("db")[0])

from uuid import uuid4
import datetime as dt
from db.models.pydantic_m import GenerationStates

from sqlalchemy import (
    BLOB,
    JSON,
    Boolean,
    Column,
    Integer,
    String,
    REAL,
    UUID as UUIDType)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

from db.utils import get_uuid, get_timestamp

Base = declarative_base()


class Process(Base):
    __tablename__ = 'process_table'

    id = Column(UUIDType(as_uuid=False), primary_key=True)
    created_at = Column(REAL, nullable=False)
    updated_at = Column(REAL, nullable=False)
    soft_delete = Column(Boolean, default=False, nullable=False)
    pid = Column(Integer, nullable=False)
    gunicorn_uid = Column(String, nullable=False)
    max_processes = Column(Integer, nullable=True)
    process_name = Column(String, nullable=True)
    process_state = Column(String, nullable=True)
    process_metadata = Column(JSON, nullable=True)


class TempImgData(Base):
    __tablename__ = 'temp_img'
    
    id = Column(UUIDType(as_uuid=False), primary_key=True, default=get_uuid)
    updated_at = Column(REAL, nullable=False)
    order_uuid =  Column(UUIDType(as_uuid=False), nullable=False)
    image_format = Column(String, nullable=False)
    image_data = Column(BLOB, nullable=False)



class ImageOrder(Base):
    """Image model

    The image order model is used to store image generation information in the database.
    The status of the order might be fulfilled, pending, or failed. 

    __tablename__: `"image_order"`

    Args:
        id (UUID): A UUID for the ImageOrder.
        created_at (float): The timestamp when the user was created.
        updated_at (float): The timestamp when the user was last updated.
        soft_delete (bool): A flag to indicate if the image has been soft-deleted.
        generation_data (JSON): The data used to generate the image.
        image_uri (Optional[str]): The URI of the image.
        generation_state (str): The state of the image generation.
        log_dict (Optional[JSON]): A dictionary containing log information.

    """
    __tablename__ = 'image_order'
    
    id = Column(UUIDType(as_uuid=False), primary_key=True, default=get_uuid)
    soft_delete = Column(Boolean, default=False, nullable=False)
    created_at = Column(REAL, default=get_timestamp, nullable=False)
    updated_at = Column(REAL, default=get_timestamp, nullable=False)

    image_uri =  Column(String, nullable=True)
    generation_data = Column(JSON, nullable=False)
    generation_state = Column(String, nullable=False)
    log_dict = Column(JSON, nullable=True)