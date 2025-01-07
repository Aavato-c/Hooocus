import logging
import os
import random
import string
from logging.handlers import RotatingFileHandler
if not os.path.exists('logs'):
    os.makedirs('logs')

from consts import LOGGING_LEVEL_STREAM, LOGGING_LEVEL_FILE

class LoggingUtil:
    def __init__(self, name):
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        name=name+random_chars
        self.logger = logging.getLogger(name)
        formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(module)s:%(lineno)d:\t%(message)s', datefmt='%m%d:%H:%M:%S')
        self.logger.setLevel(logging.DEBUG)
        
        file_handler = RotatingFileHandler('logs/h3.log', maxBytes=150_000_000, backupCount=3) # 150 MB
        file_handler.setLevel(LOGGING_LEVEL_FILE)
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(LOGGING_LEVEL_STREAM)
        
        self.logger.addHandler(stream_handler)

    def get_logger(self):
        return self.logger
