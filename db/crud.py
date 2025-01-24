import os, sys

import psutil

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURR_DIR.split("db")[0])

import datetime
from time import perf_counter
from typing import Union

from sqlalchemy.orm import Session
from sqlalchemy import UUID as UUIDType

from db.database import get_db_unmanaged
from db.utils import get_timestamp
from db.models import pydantic_m as pm
from db.models import sqlalchemy_m as sm

from h3_utils.flags import OutputFormat
from h3_utils.config import ImageGenerationObjectForRequests
from h3_utils.logging_util import LoggingUtil
from h3_utils.path_configs import FolderPathsConfig

OUTPUT_DIR = FolderPathsConfig.path_outputs

log = LoggingUtil(__name__).get_logger()


# =============================================================================
#    Image order functions
# =============================================================================
def add_imageorder(
    db: Session,
    order_data: ImageGenerationObjectForRequests,
    optional_uuid: UUIDType = None,
) -> UUIDType:
    """Add a new image order to the database

    Args:
        db (Session): SQLAlchemy Session
        order_data (pm.ImageOrderInCreate): Image order data

    Returns:
        uuid_of_new_order (UUID): The ID of the new image order
    """
    try:
        log.debug(
            f"Adding new image order. Order uid: {order_data.uid}. Imagetask seed: {order_data.seed}"
        )
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


def update_imageorder_status(
    db: Session, order_id: UUIDType, status: pm.GenerationStates.Lit, uri: str = None
) -> bool:
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
            updated_order = (
                db.query(sm.ImageOrder).filter(sm.ImageOrder.id == order_id).first()
            )
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
        generation_state = (
            db.query(sm.ImageOrder.generation_state)
            .filter(sm.ImageOrder.id == order_id)
            .first()
        )
        if generation_state is None:
            return "not_found"
        return generation_state[0]
    except Exception as e:
        log.error(f"Error getting image URL: {e}")
        raise e


def update_inmem_img_cache(
    db: Session, order_id: UUIDType, img_data: bytearray, img_format: str
) -> bool:
    log.debug(f"Updating in-memory image cache for order: {order_id}")
    try:
        start_time = perf_counter()
        data_to_add = pm.TempImgDataAdd(
            order_uuid=order_id,
            image_format=img_format,
            image_data=img_data,
            updated_at=get_timestamp(),
        )
        log.debug(f"Adding temp image data with updated_at: {data_to_add.updated_at}")
        data_to_add = sm.TempImgData(**data_to_add.model_dump())
        log.debug(data_to_add.updated_at)
        db.add(data_to_add)
        db.commit()
        log.debug(
            f"Time taken to update in-memory image cache: {perf_counter() - start_time}"
        )
        return True
    except Exception as e:
        log.error(f"Error updating in-memory image cache: {e}")
        raise e


def get_temp_img_for_order(
    inmem_db: Session, order_id: UUIDType, finished: bool = False
) -> Union[bytearray, str] | None:
    try:
        start_time = perf_counter()
        if finished:
            nofile = True
            for outputformat in OutputFormat.all:
                try:
                    with open(
                        f"{OUTPUT_DIR}/{order_id}.{outputformat}", "rb"
                    ) as f:  # TOOD Handle format change
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
            img_data, img_format, updated_at = (
                inmem_db.query(
                    sm.TempImgData.image_data,
                    sm.TempImgData.image_format,
                    sm.TempImgData.updated_at,
                )
                .filter(sm.TempImgData.order_uuid == order_id)
                .order_by(sm.TempImgData.updated_at.desc())
                .first()
            )
            log.debug(
                f"Image update time: {datetime.datetime.fromtimestamp(updated_at)}"
            )
            if img_data is None:
                return None
            log.debug(
                f"Time taken to get in-memory image cache: {perf_counter() - start_time}"
            )
            return img_data, img_format
    except Exception as e:
        log.error(f"Error getting in-memory image cache: {e}")
        raise e


def clear_cache_for_temp_img(db: Session, order_id: UUIDType | str) -> bool:
    try:
        start_time = perf_counter()
        db.query(sm.TempImgData).filter(sm.TempImgData.order_uuid == order_id).delete()
        db.commit()
        log.debug(
            f"Time taken to clear in-memory image cache: {perf_counter() - start_time}"
        )
        return True
    except Exception as e:
        log.error(f"Error clearing in-memory image cache: {e}")
        raise e


def add_process(
    pid: int,
    guni_uid: str,
    max_processes: int,
    process_name: str = "H3_proc",
    process_metadata: dict = {},
    process_state: str = pm.ProcessStates.running,
) -> UUIDType:
    try:
        try:
            db = get_db_unmanaged()
            new_process = pm.ProcessInCreate(
                pid=pid,
                gunicorn_uid=guni_uid,
                max_processes=max_processes,
                process_name=process_name,
                process_metadata=process_metadata,
                process_state=process_state,
            )
            new_process_to_add = sm.Process(**new_process.model_dump())
            db.add(new_process_to_add)
            db.commit()
        finally:
            db.close()

        return new_process.id
    except Exception as e:
        log.error(f"Error adding process: {e}")
        raise e
    
def modify_process_state(db: Session, process_in_update: pm.ProcessInUpdate) -> bool:
    try:
        db.query(sm.Process).filter(sm.Process.id == process_in_update.id).update(**process_in_update.model_dump())
        db.commit()
        return True
    except Exception as e:
        log.error(f"Error modifying process state: {e}")
        return False
    
def get_processes_by_guni_id(db: Session, guni_id: str) -> list[pm.ProcessInDb]:
    try:
        processes = db.query(sm.Process).filter(sm.Process.gunicorn_uid == guni_id).all()
        return [pm.ProcessInDb.model_validate(process) for process in processes]
    except Exception as e:
        log.error(f"Error getting processes by gunicorn ID: {e}")
        raise e
    
def kill_all_processes_not_matching_guni_id(guni_id: str, dry_run: bool = False) -> bool:
    try:
        db = get_db_unmanaged()
        processes_not_matching = db.query(sm.Process).filter(sm.Process.gunicorn_uid != guni_id, sm.Process.soft_delete == False).all()
        if not processes_not_matching or len(processes_not_matching) == 0:
            log.warning("No processes found to kill")
            return True
        
        for process in processes_not_matching:
            process_exists = psutil.pid_exists(process.pid)
            if not process_exists:
                log.warning(f"Process with PID: {process.pid} does not exist")
                if not dry_run:
                    process.soft_delete = True
                    process.updated_at = get_timestamp()
                    db.commit()
                else:
                    log.warning("Dry run, not removing reduntant process")
                continue
            if not dry_run:
                log.warning(f"Killing process with PID: {process.pid}")
                os.system(f"kill {process.pid}")
                process.soft_delete = True
                process.updated_at = get_timestamp()
                db.commit()
                log.warning(f"Killed process with PID: {process.pid}. (By process pid: {os.getpid()})")
            else:
                log.warning(f"Dry run, not killing process with PID: {process.pid}")
        db.close()
        return True
    except Exception as e:
        log.error(f"Error killing processes not matching gunicorn ID: {e}")
        db.close()
        return False
    finally:
        db.close()


            
        



    


if __name__ == "__main__":
    add_process(123, "123", 123, "123", {"123": 123})
