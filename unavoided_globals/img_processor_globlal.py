import datetime
import os, sys

from db import crud
from db.models.pydantic_m import ProcessStates
from unavoided_globals import shared

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

import threading
from unavoided_globals.global_model_management import global_model_management

from h3_utils.logging_util import LoggingUtil
log = LoggingUtil(__name__).get_logger()


def create_image_processor(guid = None):
    from modules.async_worker import ImageTaskProcessor
    if guid is not None:
        shared.GLOBAL_GUNICORN_ID = guid
        shared.INSTANCE_COUNT = 1
        log.warning(f"GUID set to {guid}.")
    if shared.IMAGE_PROCESSOR:
        log.warning("Image processor already exists.")
        return
    else:
        pid = os.getpid()

        if not crud.add_process(
            pid=pid,
            guni_uid=shared.GLOBAL_GUNICORN_ID,
            max_processes=shared.MAX_PROCESSES,
            process_name="ImageTaskProcessor",
            process_metadata={
                "instance_count": shared.INSTANCE_COUNT,
                "start_time": datetime.datetime.now().isoformat(),
            },
            process_state=ProcessStates.running,
        ):
            log.error("Error adding process to database.")
            sys.exit(1)

        log.warning("Creating image processor.")
        # GLOBAL VAR USAGE (SET)
        shared.IMAGE_PROCESSOR = ImageTaskProcessor(global_uuid=shared.GLOBAL_GUNICORN_ID, max_processes=shared.MAX_PROCESSES, instance_count=shared.INSTANCE_COUNT)
        global_model_management.interrupt_processing = False
        # GLOBAL VAR USAGE (SET)
        shared.IMAGE_PROCESSOR.reset_cuda_memory()
        # GLOBAL VAR USAGE (SET)
        threading.Thread(target=shared.IMAGE_PROCESSOR.process_all_tasks, daemon=True).start()
        pid = os.getpid()
        log.warning(f"Image processor generated in GLOBAL with PID: {pid}")
