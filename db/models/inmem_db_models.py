import os, sys

from pydantic import BaseModel
from regex import B

from db.models.pydantic_m import GenerationStates
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURR_DIR.split("db")[0])

from uuid import uuid4
import datetime as dt

from sqlalchemy import (
    BLOB,
    JSON,
    Boolean,
    Column,
    String,
    REAL,
    UUID as UUIDType)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

from db.utils import get_uuid

InMemBase = declarative_base()


class TempImgData(InMemBase):
    __tablename__ = 'temp_img'
    
    id = Column(UUIDType(as_uuid=False), primary_key=True, default=get_uuid())
    updated_at = Column(REAL, nullable=False, default=dt.datetime.now().timestamp())
    order_uuid =  Column(UUIDType(as_uuid=False), nullable=False)
    image_format = Column(String, nullable=False)
    image_data = Column(BLOB, nullable=False)

#Pydantic model
class TempImgDataAdd(BaseModel):
    order_uuid: str
    image_format: str
    image_data: bytes

class TempImgDataReturn(BaseModel):
    id: str
    updated_at: float
    order_uuid: str
    image_format: str
    image_data: bytes


  