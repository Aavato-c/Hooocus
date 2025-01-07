
import os, sys

from unavoided_globals import shared

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

import threading
from modules.async_worker import ImageTaskProcessor
from unavoided_globals.global_model_management import global_model_management

from h3_utils.logging_util import LoggingUtil
log = LoggingUtil(__name__).get_logger()


def create_image_processor():
    if shared.IMAGE_PROCESSOR:
        log.warning("Image processor already exists.")
        return
    else:
        log.warning("Creating image processor.")
        # GLOBAL VAR USAGE (SET)
        shared.IMAGE_PROCESSOR = ImageTaskProcessor(global_uuid=shared.GLOBAL_GUNICORN_ID, max_processes=shared.MAX_PROCESSES)
        global_model_management.interrupt_processing = False
        # GLOBAL VAR USAGE (SET)
        shared.IMAGE_PROCESSOR.reset_cuda_memory()
        # GLOBAL VAR USAGE (SET)
        threading.Thread(target=shared.IMAGE_PROCESSOR.process_all_tasks, daemon=True).start()
        pid = os.getpid()
        log.warning(f"Image processor generated in GLOBAL with PID: {pid}")







