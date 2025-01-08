import datetime
import re
import os, sys
import json
from time import perf_counter
from typing import Literal, Union

from db.database import get_db_unmanaged
from h3_utils.flags import OutputFormat
from h3_utils.config import ImageGenerationObjectForRequests


CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURR_DIR.split("db")[0])

from sqlalchemy.orm import Session
from sqlalchemy import UUID as UUIDType

from db.utils import get_timestamp
from db.models import pydantic_m as pm
from db.models import sqlalchemy_m as sm
from db.models.inmem_db_models import TempImgDataAdd, TempImgDataReturn, TempImgData

from h3_utils.logging_util import LoggingUtil
from h3_utils.path_configs import FolderPathsConfig

OUTPUT_DIR = FolderPathsConfig.path_outputs

log = LoggingUtil(__name__).get_logger()


# =============================================================================
#    Image order functions
# =============================================================================
def add_imageorder(db: Session, order_data: ImageGenerationObjectForRequests, optional_uuid: UUIDType = None) -> UUIDType:
    """Add a new image order to the database

    Args:
        db (Session): SQLAlchemy Session
        order_data (pm.ImageOrderInCreate): Image order data
        
    Returns:
        uuid_of_new_order (UUID): The ID of the new image order
    """
    try:
        log.debug(f"Adding new image order. Order uid: {order_data.uid}. Imagetask seed: {order_data.seed}")
        new_order = pm.ImageOrderInCreate(generation_data=order_data.model_dump_json())
        new_order_to_add = sm.ImageOrder(**new_order.model_dump())
        
        if optional_uuid is not None:
            log.warning(f"Optional UUID provided: {optional_uuid}")
            new_order_to_add.id = optional_uuid
        else:
            log.warning("No optional UUID provided")
            new_order_to_add.id = new_order.id

        uuid_of_new_order = new_order_to_add.id
        log.warning(f"Adding new image order with uid: {uuid_of_new_order}")
        db.add(new_order_to_add)
        db.commit()
        return uuid_of_new_order
    except Exception as e:
        log.error(f"Error adding event: {e}")
        raise e

def update_imageorder_status(db: Session, order_id: UUIDType, status: pm.GenerationStates.Lit, uri: str = None) -> bool:
    """Update the status of an image order

    Args:
        db (Session): SQLAlchemy Session
        order_id (UUID): The ID of the image order
        status (pm.GenerationStates.Lit): The status of the image order
        uri (Optional[str], None): The URI of the image, default is None
        
    Returns:
        bool: True if successful 

    Raises:
        Exception: If an error occurs
    """
    try:
        order = db.query(sm.ImageOrder).filter(sm.ImageOrder.id == order_id).first()
        order.generation_state = status
        order.image_uri = uri
        order.updated_at = get_timestamp()
        db.commit()

        # =====================================================================
        # Can be removed later
        try:
            # Check if the order has been updated
            updated_order = db.query(sm.ImageOrder).filter(sm.ImageOrder.id == order_id).first()
            if updated_order.generation_state != status:
                raise Exception("Failed to update image order status")
        except Exception as e:
            log.error(f"Error updating image order status: {e}")
            raise e
        # =====================================================================
            
        return True
    except Exception as e:
        log.error(f"Error updating image order status: {e}")
        raise e
    
def update_imageorder_log(order_id: UUIDType, log_data: str) -> bool:
    """Update the log of an image order

    Args:
        order_id (UUID): The ID of the image order
        log_data (str): The log data
        
    Returns:
        bool: True if successful 

    Raises:
        Exception: If an error occurs
    """
    db = get_db_unmanaged()
    try:
        order = db.query(sm.ImageOrder).filter(sm.ImageOrder.id == order_id).first()
        order.log_dict = log_data
        order.updated_at = get_timestamp()
        db.commit()
        db.close()
        db = None
        return True
    except Exception as e:
        log.error(f"Error updating image order log: {e}")
        return False
    finally:
        log.debug("Closing db connection in update_imageorder_log")
        if db is not None:
            db.close()
    
def get_imageorder(db: Session, order_id: UUIDType) -> pm.ImageOrderInResponse:
    """Get an image order from the database

    Args:
        db (Session): SQLAlchemy Session
        order_id (UUID): The ID of the image order
        
    Returns:
        pm.ImageOrderInResponse: The image order

    """
    try:
        order = db.query(sm.ImageOrder).filter(sm.ImageOrder.id == order_id).first()
        if order is None:
            log.error(f"Image order not found: {order_id}")
            return False
        return pm.ImageOrderInResponse.model_validate(order)
    except Exception as e:
        log.error(f"Error getting image order: {e}")
        raise e    

def should_generate_or_url(db: Session, order_id: UUIDType) -> pm.GenerationStates.Lit:
    """Check if an image order should be generated or if the URL should be returned

    Args:
        db (Session): SQLAlchemy Session
        order_id (UUID): The ID of the image order
        
    Returns:
        Literal["generate", "url", "not_found"]: "generate" if the image should be generated, "url" if the URL should be returned, "not_found" if the image order is not found

    Raises:
        Exception: If an error occurs
    """
    try:
        generation_state = db.query(sm.ImageOrder.generation_state).filter(sm.ImageOrder.id == order_id).first()
        if generation_state is None:
            return "not_found"
        return generation_state[0]
    except Exception as e:
        log.error(f"Error getting image URL: {e}")
        raise e
    

def update_inmem_img_cache(inmem_db: Session, order_id: UUIDType, img_data: bytearray, img_format: str) -> bool:
    log.debug(f"Updating in-memory image cache for order: {order_id}")
    try:
        start_time = perf_counter()
        data_to_add = TempImgDataAdd(order_uuid=order_id, image_format=img_format, image_data=img_data, updated_at=get_timestamp())
        log.debug(f"Adding temp image data with updated_at: {data_to_add.updated_at}")
        data_to_add = TempImgData(**data_to_add.model_dump())
        log.debug(data_to_add.updated_at)
        inmem_db.add(data_to_add)
        inmem_db.commit()
        log.debug(f"Time taken to update in-memory image cache: {perf_counter() - start_time}")
        return True
    except Exception as e:
        log.error(f"Error updating in-memory image cache: {e}")
        raise e
    
def get_temp_img_for_order(inmem_db: Session, order_id: UUIDType, finished: bool = False) -> Union[bytearray, str] | None:
    try:
        start_time = perf_counter()
        if finished: 
            nofile = True
            for outputformat in OutputFormat.all:
                try:
                    with open(f"{OUTPUT_DIR}/{order_id}.{outputformat}", "rb") as f: #TOOD Handle format change
                        img_data = f.read()
                        img_format = outputformat
                        nofile = False
                        break
                except FileNotFoundError:
                    pass
            if nofile:
                raise FileNotFoundError(f"File not found for order: {order_id}")
            return img_data, img_format

        else:            
            img_data, img_format, updated_at = inmem_db.query(TempImgData.image_data, TempImgData.image_format, TempImgData.updated_at).filter(TempImgData.order_uuid == order_id).order_by(TempImgData.updated_at.desc()).first()
            log.debug(f"Image update time: {datetime.datetime.fromtimestamp(updated_at)}")
            if img_data is None:
                return None
            log.debug(f"Time taken to get in-memory image cache: {perf_counter() - start_time}")
            return img_data, img_format
    except Exception as e:
        log.error(f"Error getting in-memory image cache: {e}")
        raise e
        
def clear_cache_for_temp_img(db: Session, order_id: UUIDType | str) -> bool:
    try:
        start_time = perf_counter()
        db.query(TempImgData).filter(TempImgData.order_uuid == order_id).delete()
        db.commit()
        log.debug(f"Time taken to clear in-memory image cache: {perf_counter() - start_time}")
        return True
    except Exception as e:
        log.error(f"Error clearing in-memory image cache: {e}")
        raise e