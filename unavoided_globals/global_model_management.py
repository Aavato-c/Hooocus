# Was in: Model modules/model_management.py
import threading

from h3_utils.logging_util import LoggingUtil

log = LoggingUtil(__name__).get_logger()


class InterruptProcessingException(Exception):
    log.info(str(Exception))
    pass


class GlobalModelManagement:
    def __init__(self):
        self.interrupt_processing_mutex = threading.RLock()
        self.interrupt_processing = False

    def interrupt_current_processing(self, value=True):
        with self.interrupt_processing_mutex:
            self.interrupt_processing = value

    def processing_interrupted(self):
        with self.interrupt_processing_mutex:
            return self.interrupt_processing

    def throw_exception_if_processing_interrupted(self):
        log.debug("Checking for interrupt")
        with self.interrupt_processing_mutex:
            if self.interrupt_processing:
                self.interrupt_processing = False
                raise InterruptProcessingException("Processing Interrupted")


global_model_management = GlobalModelManagement()
