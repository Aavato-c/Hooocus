import os, sys
import json
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURR_DIR.split("db")[0])

from sqlalchemy.orm import Session
from sqlalchemy import UUID as UUIDType

from db.models import pydantic_m as pm
from db.models import sqlalchemy_m as sm

from h3_utils.logging_util import LoggingUtil

log = LoggingUtil(__name__).get_logger()

# =============================================================================
#    Image order functions
# =============================================================================
def add_imageorder(db: Session, order_data: pm.ImageOrderInCreate) -> pm.ImageOrderInResponse:
    """Add a new image order to the database

    Args:
        db (Session): SQLAlchemy Session
        order_data (pm.ImageOrderInCreate): Image order data
        
    Returns:
        bool: True if successful 

    Raises:
        Exception: If an error occurs
    """
    try:
        new_order = sm.ImageOrder(**order_data.model_dump())
        db.add(new_order)
        db.commit()
        return True
    except Exception as e:
        log.error(f"Error adding event: {e}")
        raise e


