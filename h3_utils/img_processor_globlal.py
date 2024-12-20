
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__).split("h3_utils")[0])))

import threading
from h3_utils.config import LAUNCH_ARGS, ImageGenerationObject, OverWriteControls, DefaultConfigImageGen, HooocusConfig
from modules.async_worker import ImageTaskProcessor
from unavoided_globals.global_model_management import global_model_management
from unavoided_globals.unavoided_global_vars import IPM

from h3_utils.logging_util import LoggingUtil
log = LoggingUtil(name="img_processor_global.py").get_logger()

class BatchTemplates:
    _shared = HooocusConfig
    _shared.image_number = 1

    normal = HooocusConfig
    

if not IPM.exists_imageprocess:
    IPM.imgProcessorGlobal = ImageTaskProcessor()
    global_model_management.interrupt_processing = False
    IPM.imgProcessorGlobal.reset_cuda_memory()
    exists_imageprocess = True
    threading.Thread(target=IPM.imgProcessorGlobal.process_all_tasks, daemon=True).start()
    log.info('Image processor started.')
    imgProcessor = IPM.imgProcessorGlobal
else:
    log.info('Image processor already exists.')
    imgProcessor = IPM.imgProcessorGlobal


