from sqlalchemy.orm import Session
from sqlalchemy import UUID as UUIDType

from db.database import get_db_unmanaged
from db.models import sqlalchemy_m as sm
from db.utils import get_timestamp

from h3_utils.logging_util import LoggingUtil

log = LoggingUtil(__name__).get_logger()

    
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