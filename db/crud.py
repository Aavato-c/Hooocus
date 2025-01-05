import re
import os, sys
import json
from typing import Literal

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURR_DIR.split("db")[0])

from sqlalchemy.orm import Session
from sqlalchemy import UUID as UUIDType

from db.utils import get_timestamp
from db.models import pydantic_m as pm
from db.models import sqlalchemy_m as sm

from h3_utils.logging_util import LoggingUtil

log = LoggingUtil(__name__).get_logger()

# =============================================================================
#    Image order functions
# =============================================================================
def add_imageorder(db: Session, order_data: pm.ImageOrderInCreate, optional_uuid: UUIDType = None) -> UUIDType:
    """Add a new image order to the database

    Args:
        db (Session): SQLAlchemy Session
        order_data (pm.ImageOrderInCreate): Image order data
        
    Returns:
        uuid_of_new_order (UUID): The ID of the new image order
    """
    try:
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

def update_imageorder_status(db: Session, order_id: UUIDType, status: bool, uri: str = None) -> bool:
    """Update the status of an image order

    Args:
        db (Session): SQLAlchemy Session
        order_id (UUID): The ID of the image order
        status (bool): The status of the image order (True if generated, False if not)
        uri (Optional[str], None): The URI of the image, default is None
        
    Returns:
        bool: True if successful 

    Raises:
        Exception: If an error occurs
    """
    try:
        order = db.query(sm.ImageOrder).filter(sm.ImageOrder.id == order_id).first()
        order.has_been_generated = status
        order.image_uri = uri
        order.updated_at = get_timestamp()
        db.commit()

        # =====================================================================
        # Can be removed later
        try:
            # Check if the order has been updated
            updated_order = db.query(sm.ImageOrder).filter(sm.ImageOrder.id == order_id).first()
            if updated_order.has_been_generated != status:
                raise Exception("Failed to update image order status")
        except Exception as e:
            log.error(f"Error updating image order status: {e}")
            raise e
        # =====================================================================
            
        return True
    except Exception as e:
        log.error(f"Error updating image order status: {e}")
        raise e
    
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

def should_generate_or_url(db: Session, order_id: UUIDType) -> Literal["generate", "url", "not_found"]:
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
        order = db.query(sm.ImageOrder).filter(sm.ImageOrder.id == order_id).first()
        if order is None:
            return "not_found"
        if order.has_been_generated:
            return "url"
        return "generate"
    except Exception as e:
        log.error(f"Error getting image URL: {e}")
        raise e